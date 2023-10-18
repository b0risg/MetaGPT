from metagpt.logs import logger
from metagpt.provider.spark_api import SparkAPI


def test_message():
    llm = SparkAPI()

    logger.info(llm.ask('只回答"收到了"这三个字。'))
    logger.info(llm.ask('从1，数到20。'))
