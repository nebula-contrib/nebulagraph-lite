FROM python:3.8-slim

# Set work directory
WORKDIR /app

# Install curl and nebulagraph-lite
RUN apt-get update && apt-get install -y curl which && \
    pip install nebulagraph-lite && \
    nebulagraph --container start && \
    nebulagraph --container stop

# Expose port 9559, 9669, 9779 for NebulaGraph
EXPOSE 9669 9559 9779

# Start NebulaGraph
CMD ["nebulagraph", "--container", "start"]

# How to run it
# docker build -t nebulagraph-lite .
# docker run -p 9669:9669 nebulagraph-lite
