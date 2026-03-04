import os

structure = {
    "": [
        ".env.example",
        "config.yaml",
        "requirements.txt",
        "main.py",
    ],
    "src": ["__init__.py"],
    "src/database": [
        "__init__.py",
        "connection.py",
        "models.py",
        "crud.py",
    ],
    "src/chunking": [
        "__init__.py",
        "parent_child.py",
        "your_strategy.py",
    ],
    "src/caching": [
        "__init__.py",
        "exact_cache.py",
        "semantic_cache.py",
        "retrieval_cache.py",
    ],
    "src/retrieval": [
        "__init__.py",
        "retriever.py",
        "reranker.py",
    ],
    "src/generation": [
        "__init__.py",
        "generator.py",
    ],
    "src/utils": [
        "__init__.py",
        "embeddings.py",
        "logger.py",
    ],
    "data": [".gitkeep"],
    "tests": [],
    "docs": ["architecture.md"],
}


def create_structure():
    for folder, files in structure.items():
        folder_path = os.path.join(folder) if folder else "."
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):  # prevent overwrite
                with open(file_path, "w") as f:
                    f.write("")

    print("project structure created")


if __name__ == "__main__":
    create_structure()