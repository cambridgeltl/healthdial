from dataset.database import HealthDialogueDatabase

if __name__ == "__main__":
    database = HealthDialogueDatabase()
    print(f"Languages: {database.support_language_list}")
    print(f"English snippets: {len(database.get_all_snippet_list_for_language('eng'))}")
