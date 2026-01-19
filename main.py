from utils import squad_json_to_dataframe


def main():
    train_path = "data/train-v2.0.json"
    df_train = squad_json_to_dataframe(train_path)

    print(f"Shape: {df_train.shape}")
    print(df_train.head())


if __name__ == "__main__":
    main()
