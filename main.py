from utils import squad_json_to_dataframe
from sklearn.model_selection import train_test_split


def main():
    train_path = "data/train-v2.0.json"
    df_train_full = squad_json_to_dataframe(train_path)
    df_train, df_val = train_test_split(df_train_full, test_size=0.1, random_state=42)

    test_path = "data/dev-v2.0.json"
    df_test = squad_json_to_dataframe(test_path)

    print(f"Shape train: {df_train.shape}")
    print(f"Shape val: {df_val.shape}")
    print(f"Shape test: {df_test.shape}")


if __name__ == "__main__":
    main()
