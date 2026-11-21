# Demucs v4 (MIT). Weights are fetched at build time into the image, so a run never downloads and
# the summary's weights_sha256 pins what was measured.
#
#   docker build -t sepbench-demucs:4.0.1-n2 runners/demucs
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

RUN pip install --no-cache-dir demucs==4.0.1 soundfile==0.12.1

RUN python -c "from demucs.pretrained import get_model; [get_model(m) for m in ('htdemucs', 'htdemucs_ft')]"

COPY separate.py /opt/sep/separate.py
ENTRYPOINT ["python", "/opt/sep/separate.py"]
