import json
import asyncio

from mybgg.downloader import Downloader
from mybgg.indexer import Indexer
from setup_logging import setup_logging
from mybgg.translator import async_process_queries

def main(args):
    SETTINGS = json.load(open("config.json", "rb"))

    downloader = Downloader(
        project_name=SETTINGS["project"]["name"],
        cache_bgg=args.cache_bgg,
        debug=args.debug,
    )
    collection = downloader.collection(
        user_name=SETTINGS["boardgamegeek"]["user_name"],
        extra_params=SETTINGS["boardgamegeek"]["extra_params"],
    )
    num_games = len(collection)
    num_expansions = sum([len(game.expansions) for game in collection])
    num_accessories = sum([len(game.accessories) for game in collection ])
    print(f"Imported {num_games} games, {num_expansions} expansions, and {num_accessories} accessories from boardgamegeek.")

    if not len(collection):
        assert False, "No games imported, is the boardgamegeek part of config.json correctly set?"
        
    description_dict = {game.id: game.description for game in collection}
    description = asyncio.run(async_process_queries(description_dict))
    for game in collection:
        game.description = description[game.id]
    
    if not args.no_indexing:
        hits_per_page = SETTINGS["algolia"].get("hits_per_page", 48)
        indexer = Indexer(
            app_id=SETTINGS["algolia"]["app_id"],
            apikey=args.apikey,
            index_name=SETTINGS["algolia"]["index_name"],
            hits_per_page=hits_per_page,
        )
        indexer.add_objects(collection)
        indexer.delete_objects_not_in(collection)

        print(f"Indexed {num_games} games, {num_expansions} expansions, and {num_accessories} accessories in algolia, and removed everything else.")
    else:
        print("Skipped indexing.")


if __name__ == '__main__':
    import argparse

    setup_logging()

    parser = argparse.ArgumentParser(description='下载并索引桌面游戏')
    parser.add_argument(
        '--apikey',
        type=str,
        required=True,
        help='您的算法站点的管理员api密钥'
    )
    parser.add_argument(
        '--no_indexing',
        action='store_true',
        help=(
            "跳过算法中的索引。这在开发过程中很有用"
            "，当您想一遍又一遍地从BGG获取数据时，"
            "并且不想用完Algolia的索引配额。"
        )
    )
    parser.add_argument(
        '--cache_bgg',
        action='store_true',
        help=(
            "为所有BGG调用启用缓存。这会使脚本在"
            "第二次运行时运行得非常快。"
        )
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help="打印调试信息，如发出的请求和收到的响应。"
    )

    args = parser.parse_args()

    main(args)
