import kfp.compiler
from kfp import dsl


@dsl.component(
    packages_to_install=["datasets"],
)
def prepare_yoda_dataset(
    yoda_train_dataset: dsl.Output[dsl.Dataset],
    yoda_eval_dataset: dsl.Output[dsl.Dataset],
    yoda_input_dataset: str = "dvgodoy/yoda_sentences",
    train_split_ratio: float = 0.8,
):
    """Prepare the training and evaluation datasets by downloading and preprocessing.

    Downloads the yoda_sentences dataset from HuggingFace, renames columns to match
    the expected format for training (prompt/completion), splits into train/eval sets,
    and saves them as output artifacts.

    Args:
        yoda_input_dataset (str): Dataset to download from HuggingFace
        yoda_train_dataset (dsl.Output[dsl.Dataset]): Output dataset for training.
        yoda_eval_dataset (dsl.Output[dsl.Dataset]): Output dataset for evaluation.
        train_split_ratio (float): Ratio for training (0.0-1.0), defaults to 0.8
    """
    from datasets import load_dataset

    # Validate inputs
    if not yoda_input_dataset or not isinstance(yoda_input_dataset, str):
        raise ValueError("yoda_input_dataset must be a non-empty string")
    
    if not (0.0 < train_split_ratio < 1.0):
        raise ValueError(f"train_split_ratio must be between 0.0 and 1.0, got {train_split_ratio}")

    print(f"Downloading and loading the dataset from {yoda_input_dataset}")
    dataset = load_dataset(yoda_input_dataset, split="train")
    print("Renaming columns")
    dataset = dataset.rename_column("sentence", "prompt")
    dataset = dataset.rename_column("translation_extra", "completion")
    dataset = dataset.remove_columns(["translation"])

    # Add prefix to prompts
    print("Adding Yoda speak prefix to prompts")

    def add_yoda_prefix(example):
        example["prompt"] = "Translate the following to Yoda speak: " + example["prompt"]
        return example

    dataset = dataset.map(add_yoda_prefix)

    # Split the dataset into train and eval sets
    print(
        f"Splitting dataset with {len(dataset)} rows into train ({train_split_ratio:.1%}) "
        f"and eval ({(1-train_split_ratio):.1%}) sets"
    )
    split_dataset = dataset.train_test_split(test_size=1 - train_split_ratio, seed=42)

    train_dataset = split_dataset["train"]
    eval_dataset = split_dataset["test"]

    print(f"Train set: {len(train_dataset)} rows")
    print(f"Eval set: {len(eval_dataset)} rows")

    # Save both datasets
    print(f"Saving train dataset to {yoda_train_dataset.path}")
    train_dataset.save_to_disk(yoda_train_dataset.path)

    print(f"Saving eval dataset to {yoda_eval_dataset.path}")
    eval_dataset.save_to_disk(yoda_eval_dataset.path)


if __name__ == "__main__":
    """Compile the component for use in pipelines.
    
    This can also be used to test the component compilation.
    """
    from pathlib import Path
    
    output_path = Path(__file__).parent / "yoda_data_processor_component.yaml"
    print(f"Compiling component to {output_path}")
    
    kfp.compiler.Compiler().compile(
        prepare_yoda_dataset,
        package_path=str(output_path),
    )
    
    print(f"✅ Component compiled successfully to {output_path}")
    print(f"   File size: {output_path.stat().st_size} bytes")
