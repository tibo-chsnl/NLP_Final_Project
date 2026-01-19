import json
import pandas as pd


def squad_json_to_dataframe(
    file_path: str,
) -> pd.DataFrame:
    """
    Parses the SQuAD dataset JSON file and converts it into a pandas DataFrame.
    """
    with open(file_path, "r") as f:
        data = json.load(f)

    rows = []

    for article in data["data"]:
        title = article["title"]
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            for qa in paragraph["qas"]:
                question = qa["question"]

                is_impossible = qa.get("is_impossible", False)

                answers = (
                    qa["answers"]
                    if not is_impossible
                    else qa["plausible_answers"]
                    if "plausible_answers" in qa
                    else []
                )

                rows.append(
                    {
                        "id": qa["id"],
                        "title": title,
                        "context": context,
                        "question": question,
                        "is_impossible": is_impossible,
                        "answers": answers,
                    }
                )

    return pd.DataFrame(rows)
