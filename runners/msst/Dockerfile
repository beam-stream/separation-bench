# ZFTurbo Music-Source-Separation-Training (MIT), pinned, with the benchmark's checkpoints baked in
# and their sha256s written to /opt/weights/SHA256SUMS at build time. Weight licences differ per
# model and are listed in THIRD-PARTY.md.
#
#   docker build -t sepbench-msst:7671fae-n2 runners/msst
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ZFTurbo/Music-Source-Separation-Training /opt/msst \
 && git -C /opt/msst checkout 7671faec526b78156f60c94a767fb243a0aaa41e

RUN pip install --no-cache-dir numpy==1.26.4 scipy soundfile ml_collections omegaconf==2.2.3 \
    einops==0.8.1 rotary_embedding_torch==0.3.5 beartype==0.14.1 hyper_connections==0.1.11 \
    librosa==0.10.2 pytorch_lightning==2.4.0 packaging pyyaml tqdm

ARG MSST=https://github.com/ZFTurbo/Music-Source-Separation-Training/releases/download
RUN mkdir -p /opt/weights && cd /opt/weights \
 && curl -fsSL -o bs_roformer_ep317.ckpt https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/model_bs_roformer_ep_317_sdr_12.9755.ckpt \
 && curl -fsSL -o melband_kim.ckpt https://huggingface.co/KimberleyJSN/melbandroformer/resolve/main/MelBandRoformer.ckpt \
 && curl -fsSL -o mdx23c_vocals.ckpt $MSST/v1.0.0/model_vocals_mdx23c_sdr_10.17.ckpt \
 && curl -fsSL -o mdx23c_vocals.yaml $MSST/v1.0.0/config_vocals_mdx23c.yaml \
 && curl -fsSL -o scnet_large_starrytong.ckpt $MSST/v1.0.9/SCNet-large_starrytong_fixed.ckpt \
 && curl -fsSL -o scnet_large_starrytong.yaml $MSST/v1.0.9/config_musdb18_scnet_large_starrytong.yaml \
 && curl -fsSL -o bandit_plus_dnr.chpt $MSST/v.1.0.3/model_bandit_plus_dnr_sdr_11.47.chpt \
 && curl -fsSL -o bandit_plus_dnr.yaml $MSST/v.1.0.3/config_dnr_bandit_bsrnn_multi_mus64.yaml \
 && curl -fsSL -o bandit_v2_multi.ckpt https://zenodo.org/api/records/12701995/files/checkpoint-multi.ckpt/content \
 && echo "fea2868787551b0cff36cfcf7c3622a3  bandit_v2_multi.ckpt" | md5sum -c - \
 && sha256sum * > SHA256SUMS

# BandIt v1's package imports its training stack at module load (losses, augmentations), although
# inference calls none of it. asteroid's pesq dependency builds from source.
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir asteroid==0.7.0 torchmetrics==0.11.4 spafe==0.3.2 pedalboard~=0.8.1 \
    torch_audiomentations fire pyloudnorm pandas torch==2.4.1 \
 && cd /opt/msst && python -c "from models.bandit.core.model import MultiMaskMultiSourceBandSplitRNNSimple; from models.bandit_v2.bandit import Bandit"

# utils/audio_utils imports matplotlib at module load, and the runner needs normalize_audio and
# denormalize_audio from that module.
RUN pip install --no-cache-dir matplotlib==3.9.2

COPY separate.py /opt/sep/separate.py
WORKDIR /opt/msst
ENTRYPOINT ["python", "/opt/sep/separate.py"]
