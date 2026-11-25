"""Trusted launcher mode shared by Primus review and Agent Mail helpers."""

import os

INFERENCE_MODE_ENV = "PRIMUS_INFERENCE_MODE"
CANONICAL_LOCAL_MODEL = "local-inference-11888"


def validate_inference_mode(mode):
    if mode not in {"local", "cloud"}:
        raise ValueError(f"{INFERENCE_MODE_ENV} must be local or cloud, got {mode!r}")
    return mode


def validate_local_model_alias(model):
    """Reject model aliases that could route a local gate to another worker."""
    value = str(model or "")
    if value != CANONICAL_LOCAL_MODEL:
        raise ValueError(
            "local Red-Team Gate inference must use "
            f"{CANONICAL_LOCAL_MODEL!r}; refusing model alias {value!r}"
        )
    return value

def add_inference_mode(parser):
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('-c', '--cloud', dest='inference_mode', action='store_const',
                       const='cloud', help='use configured cloud inference explicitly; never try local')
    modes.add_argument('-l', '--local', dest='inference_mode', action='store_const',
                       const='local', help='use local inference only; fail without cloud fallback')
    parser.set_defaults(inference_mode=None)


def parse_inference_args(parser, argv=None):
    """Explicit CLI > inherited environment > local; export only after validation."""
    args = parser.parse_args(argv)
    mode = args.inference_mode
    if mode is None:
        mode = os.environ.get(INFERENCE_MODE_ENV, "local")
    try:
        args.inference_mode = validate_inference_mode(mode)
    except ValueError as exc:
        parser.error(str(exc))
    os.environ[INFERENCE_MODE_ENV] = args.inference_mode
    return args


def child_mode_args(args):
    return ['--' + validate_inference_mode(args.inference_mode)]
