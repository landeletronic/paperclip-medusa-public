# Staging do auxiliar local — llama.cpp VULKAN pinado por commit (plano padrão, Fase 1)
#
# ATENÇÃO: o plano padrão exige VULKAN (não ROCm — gfx1012 não está no rocBLAS;
# mascarar como gfx1030 causou MEMORY_APERTURE_VIOLATION). Este build usa o backend
# Vulkan do llama.cpp com Mesa/RADV no runtime.
#
# Build:  docker build -t medusa-llama-vulkan:<sha> --build-arg LLAMA_CPP_SHA=<commit> .
# Uso:    ver README.md (container com SOMENTE o render node da RX 5500).

FROM ubuntu:24.04 AS build
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential cmake libvulkan-dev glslc glslang-tools spirv-headers spirv-tools pkg-config ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ARG LLAMA_CPP_SHA=31953bcf74ba489a8bbb0c936c5fcf24fcf9485c
# hadolint ignore=DL3003
RUN git clone https://github.com/ggml-org/llama.cpp /src \
    && cd /src \
    && git checkout "${LLAMA_CPP_SHA}" \
    && git submodule update --init
RUN cmake -S /src -B /src/build \
      -DGGML_VULKAN=ON -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /src/build --config Release --target llama-server -j"$(nproc)" \
    && mkdir -p /out && cp -a /src/build/bin/. /out/ \
    && (cp -a /src/build/lib/. /out/ 2>/dev/null || true)

FROM ubuntu:24.04
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      libvulkan1 mesa-vulkan-drivers libgomp1 libstdc++6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /out /opt/llama/bin
ENV PATH=/opt/llama/bin:$PATH \
    LD_LIBRARY_PATH=/opt/llama/bin
ARG LLAMA_CPP_SHA=31953bcf74ba489a8bbb0c936c5fcf24fcf9485c
LABEL org.opencontainers.image.title="medusa-helper-staging (llama.cpp Vulkan)" \
      llama.cpp.commit="${LLAMA_CPP_SHA}" \
      backend="vulkan" \
      fase="1 (plano padrao - helper local RX 5500)"
