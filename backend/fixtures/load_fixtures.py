import asyncio
import json
import os
import sys

# для успешного импорта библиотек при запуске из терминала
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.repository.genre import GenreRepository


async def write_fixture(data: dict, repo_func):
    res = await repo_func(**data)
    return res


async def find_fixtures_path_n_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_directory = script_dir
    fix_files = [file for file in os.listdir(fixtures_directory)
                 if file.endswith('.json')]

    return fixtures_directory, fix_files


async def run():
    known_repo_for_fixture = {
        'genres.json': GenreRepository().create_genre,
    }

    fixtures_directory, fix_files = await find_fixtures_path_n_files()
    for file in fix_files:
        print(file)
        with open(os.path.join(fixtures_directory, file), 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                for line in data:
                    try:
                        await write_fixture(line, known_repo_for_fixture[file])
                        print(line.items())
                    except ValueError as e:
                        print(f'{e}. INFO: {file} - {line.items()}')
            else:
                raise AttributeError(f"{file} not in right fixture format. List must be in.")


if __name__ == '__main__':
    asyncio.run(run())
