FROM python:3.11-slim
WORKDIR /app
COPY tests_agent.py agent.py
ENV TEST_INPUTS_PATH=/workspace/test_inputs.json
ENV RESULTS_PATH=/workspace/results.json
CMD ["python", "agent.py"]
