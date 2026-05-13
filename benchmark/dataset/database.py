import os
import json

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "who_database.json",
)


class HealthDialogueDatabase:

    def __init__(self, db_path=DEFAULT_DB_PATH, load_parallel_data=True):

        self.db_path = db_path


        # Load database data
        self.language_snippet_list_dic, self.support_language_list, self.unique_id_snippet_dic, self.parallel_id_snippet_dic = self._load_data(load_parallel_data = load_parallel_data)

    def _load_data(self, load_parallel_data = True):

        language_snippet_list_dic = {}

        with open(self.db_path, "r") as f:
            raw_data = json.load(f)

        if load_parallel_data:
            raw_data = list(filter(lambda x : x["parallel_data"], raw_data))

        for item in raw_data:
            this_snippet_list = language_snippet_list_dic.get(item["language"].lower(), [])
            this_snippet_list.append(item)
            language_snippet_list_dic[item["language"].lower()] = this_snippet_list

        if load_parallel_data:
            lengths = [len(lst) for lst in language_snippet_list_dic.values()]
            assert all(length == lengths[0] for length in lengths), "Not all parallel lists have the same length"

        support_language_list = list(language_snippet_list_dic.keys())

        unique_id_snippet_dic = {}
        parallel_id_snippet_dic = {}
        for language in support_language_list:
            snippet_list =  language_snippet_list_dic[language]
            for snippet in snippet_list:
                unique_id = snippet["unique_identifier"]
                assert unique_id not in unique_id_snippet_dic
                unique_id_snippet_dic[unique_id] = snippet

                if snippet["parallel_data"]:
                    assert snippet["parallel_identifier"]

                    this_language_snippet_dic = parallel_id_snippet_dic.get(snippet["parallel_identifier"], {})
                    this_language_snippet_dic[language] = snippet
                    parallel_id_snippet_dic[snippet["parallel_identifier"]] = this_language_snippet_dic

        for parallel_id, language_snippet_dic in parallel_id_snippet_dic.items():
            for language in support_language_list:
                assert language in language_snippet_dic

        return language_snippet_list_dic, support_language_list, unique_id_snippet_dic, parallel_id_snippet_dic



    def get_all_snippet_list_for_language(self, language):
        language = language.lower()
        assert language in self.support_language_list
        return self.language_snippet_list_dic[language]

    def query_with_parallel_id_with(self, parallel_id):
        assert parallel_id in self.parallel_id_snippet_dic
        return self.parallel_id_snippet_dic[parallel_id]

    def query_with_unique_id_with(self, unique_id):
        assert unique_id in self.unique_id_snippet_dic
        return self.unique_id_snippet_dic[unique_id]

if __name__ == '__main__':
    this_database = HealthDialogueDatabase()
    print(this_database.query_with_parallel_id_with("fact-sheets/detail/yaws::7")["eng"])
    print(this_database.query_with_unique_id_with("54dcf807-1bde-496a-9332-dff93c83b43f"))
    print(len(this_database.get_all_snippet_list_for_language("eng")))
