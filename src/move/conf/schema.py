__all__ = [
    "MOVEConfig",
    "EncodeDataConfig",
    "IdentifyAssociationsConfig",
    "IdentifyAssociationsBayesConfig",
    "IdentifyAssociationsTTestConfig",
]

from dataclasses import dataclass, field

from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf, MISSING
from typing import Any, Optional

from move.models.vae import VAE
from move.training.training_loop import training_loop


def get_fully_qualname(sth: Any) -> str:
    return ".".join((sth.__module__, sth.__qualname__))


@dataclass
class InputConfig:
    name: str
    weight: float = 1.0


@dataclass
class DataConfig:
    user_conf: str
    na_value: str
    raw_data_path: str
    interim_data_path: str
    processed_data_path: str
    headers_path: str
    version: str
    ids_file_name: str
    ids_has_header: bool
    ids_colname: str
    categorical_inputs: list[InputConfig]
    continuous_inputs: list[InputConfig]
    data_of_interest: str
    categorical_names: list[str]
    continuous_names: list[str]
    categorical_weights: list[float]
    continuous_weights: list[float]
    data_features_to_visualize_notebook4: list[str]
    write_omics_results_notebook5: list[str]


@dataclass
class ModelConfig:
    _target_: str = MISSING
    cuda: bool = MISSING


@dataclass
class VAEConfigDeprecated(ModelConfig):
    user_conf: str = MISSING
    seed: int = MISSING
    cuda: bool = MISSING
    lrate: float = MISSING
    num_epochs: int = MISSING
    patience: int = MISSING
    kld_steps: list[int] = MISSING
    batch_steps: list[int] = MISSING


@dataclass
class VAEConfig(ModelConfig):
    """Configuration for the VAE module."""

    _target_: str = get_fully_qualname(VAE)
    categorical_weights: list[int] = MISSING
    continuous_weights: list[int] = MISSING
    num_hidden: list[int] = MISSING
    num_latent: int = MISSING
    beta: float = MISSING
    dropout: float = MISSING
    cuda: bool = False


@dataclass
class TuningReconstructionConfig:
    user_config: str
    num_hidden: list[int]
    num_latent: list[int]
    num_layers: list[int]
    beta: list[float]
    dropout: list[float]
    batch_sizes: list[int]
    repeats: int
    max_param_combos_to_save: int


@dataclass
class TuningStabilityConfig:
    user_config: str
    num_hidden: list[int]
    num_latent: list[int]
    num_layers: list[int]
    beta: list[float]
    dropout: list[float]
    batch_sizes: list[int]
    repeat: int
    tuned_num_epochs: int


@dataclass
class TrainingLatentConfig:
    user_config: str
    num_hidden: int
    num_latent: int
    num_layers: int
    dropout: float
    beta: float
    batch_sizes: int
    tuned_num_epochs: int


@dataclass
class TrainingAssociationConfig:
    user_config: str
    num_hidden: int
    num_latent: list[int]
    num_layers: int
    dropout: float
    beta: float
    batch_sizes: int
    repeats: int
    tuned_num_epochs: int


@dataclass
class TrainingLoopConfig:
    _target_: str = get_fully_qualname(training_loop)
    num_epochs: int = MISSING
    lr: float = MISSING
    kld_warmup_steps: list[int] = MISSING
    batch_dilation_steps: list[int] = MISSING
    early_stopping: bool = MISSING
    patience: int = MISSING


@dataclass
class TaskConfig:
    """Configuration for a MOVE task.

    Attributes:
        batch_size: Number of samples in a training batch.
        model: Configuration for a model.
        training_loop: Configuration for a training loop.
    """

    batch_size: Optional[int]
    model: Optional[VAEConfig]
    training_loop: Optional[TrainingLoopConfig]


@dataclass
class EncodeDataConfig(TaskConfig):
    """Configuration for a data-encoding task."""

    batch_size = None
    model = None
    training_loop = None


@dataclass
class IdentifyAssociationsConfig(TaskConfig):
    """Configure the "identify associations" task.

    Attributes:
        target_dataset:
            Name of categorical dataset to perturb.
        target_value:
            The value to change to. It should be a category name. 
        num_refits:
            Number of times to refit the model.
        sig_threshold:
            Threshold used to determine whether an association is significant.
            In the t-test approach, this is called significance level (alpha).
            In the probabilistc approach, significant associations are selected
            if their FDR is below this threshold.

            This value should be within the range [0, 1].
        save_models:
            Whether to save the weights of each refit. If weights are saved,
            rerunning the task will load them instead of training.
    """

    target_dataset: str = MISSING
    target_value: str = MISSING
    num_refits: int = MISSING
    sig_threshold: float = 0.05
    save_refits: bool = False


@dataclass
class IdentifyAssociationsBayesConfig(IdentifyAssociationsConfig):
    """Configure the probabilistic approach to identify associations."""

    ...


@dataclass
class IdentifyAssociationsTTestConfig(IdentifyAssociationsConfig):
    """Configure the t-test approach to identify associations.

    Args:
        num_latent:
            List of latent space dimensions to train. It should contain four
            elements.
    """

    num_latent: list[int] = MISSING


@dataclass
class MOVEConfig:
    defaults: list[Any] = field(default_factory=lambda: [dict(data="base_data")])
    data: DataConfig = MISSING
    task: TaskConfig = MISSING
    model: VAEConfigDeprecated = MISSING
    tune_reconstruction: TuningReconstructionConfig = MISSING
    tune_stability: TuningStabilityConfig = MISSING
    train_latent: TrainingLatentConfig = MISSING
    train_association: TrainingAssociationConfig = MISSING
    name: str = MISSING


def extract_weights(configs: list[InputConfig]) -> list[float]:
    """Extracts the weights from a list of input configs."""
    return [item.weight for item in configs]


def extract_names(configs: list[InputConfig]) -> list[str]:
    """Extracts the weights from a list of input configs."""
    return [item.name for item in configs]


# Store config schema
cs = ConfigStore.instance()
cs.store(name="config_schema", node=MOVEConfig)
cs.store(
    group="task",
    name="encode_data",
    node=EncodeDataConfig,
)
cs.store(
    group="task",
    name="identify_associations_bayes_schema",
    node=IdentifyAssociationsBayesConfig,
)
cs.store(
    group="task",
    name="identify_associations_ttest_schema",
    node=IdentifyAssociationsTTestConfig,
)

# Register custom resolvers
OmegaConf.register_new_resolver("weights", extract_weights)
OmegaConf.register_new_resolver("names", extract_names)
