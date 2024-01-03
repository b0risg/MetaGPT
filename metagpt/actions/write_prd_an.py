#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/14 11:40
@Author  : alexanderwu
@File    : write_prd_an.py
"""
from typing import List

from metagpt.actions.action_node import ActionNode
from metagpt.logs import logger

LANGUAGE = ActionNode(
    key="Language",
    expected_type=str,
    instruction="Provide the language used in the project, typically matching the user's requirement language.",
    example="en_us",
)

PROGRAMMING_LANGUAGE = ActionNode(
    key="Programming Language",
    expected_type=str,
    instruction="Python/JavaScript or other mainstream programming language.",
    example="Python",
)

ORIGINAL_REQUIREMENTS = ActionNode(
    key="Original Requirements",
    expected_type=str,
    instruction="Place the original user's requirements here.",
    example="Create a 2048 game",
)

REFINED_REQUIREMENTS = ActionNode(
    key="Refined Requirements",
    expected_type=str,
    instruction="Update and expand the original user's requirements to reflect the evolving needs of the project."
    "Retain any content unrelated to incremental development",
    example="Create a 2048 game with a new feature that ...",
)

PROJECT_NAME = ActionNode(
    key="Project Name",
    expected_type=str,
    instruction="According to the content of \"Original Requirements,\" name the project using snake case style , like 'game_2048' or 'simple_crm.",
    example="game_2048",
)

PRODUCT_GOALS = ActionNode(
    key="Product Goals",
    expected_type=List[str],
    instruction="Provide up to three clear, orthogonal product goals.",
    example=["Create an engaging user experience", "Improve accessibility, be responsive", "More beautiful UI"],
)

REFINED_PRODUCT_GOALS = ActionNode(
    key="Refined Product Goals",
    expected_type=List[str],
    instruction="Update and expand the original product goals to reflect the evolving needs due to incremental "
    "development.Ensure that the refined goals align with the current project direction and contribute to its success."
    "Retain any content unrelated to incremental development",
    example=[
        "Enhance user engagement through new features",
        "Optimize performance for scalability",
        "Integrate innovative UI enhancements",
    ],
)

USER_STORIES = ActionNode(
    key="User Stories",
    expected_type=List[str],
    instruction="Provide up to 3 to 5 scenario-based user stories.",
    example=[
        "As a player, I want to be able to choose difficulty levels",
        "As a player, I want to see my score after each game",
        "As a player, I want to get restart button when I lose",
        "As a player, I want to see beautiful UI that make me feel good",
        "As a player, I want to play game via mobile phone",
    ],
)

REFINED_USER_STORIES = ActionNode(
    key="Refined User Stories",
    expected_type=List[str],
    instruction="Update and expand the original scenario-based user stories to reflect the evolving needs due to "
    "incremental development, no less than 5. Ensure that the refined user stories capture incremental features and "
    "improvements. Retain any content unrelated to incremental development",
    example=[
        "As a player, I want to choose difficulty levels to challenge my skills",
        "As a player, I want a visually appealing score display after each game for a better gaming experience",
        "As a player, I want a convenient restart button displayed when I lose to quickly start a new game",
        "As a player, I want an enhanced and aesthetically pleasing UI to elevate the overall gaming experience",
        "As a player, I want the ability to play the game seamlessly on my mobile phone for on-the-go entertainment",
    ],
)

COMPETITIVE_ANALYSIS = ActionNode(
    key="Competitive Analysis",
    expected_type=List[str],
    instruction="Provide 5 to 7 competitive products.",
    example=[
        "2048 Game A: Simple interface, lacks responsive features",
        "play2048.co: Beautiful and responsive UI with my best score shown",
        "2048game.com: Responsive UI with my best score shown, but many ads",
    ],
)

COMPETITIVE_QUADRANT_CHART = ActionNode(
    key="Competitive Quadrant Chart",
    expected_type=str,
    instruction="Use mermaid quadrantChart syntax. Distribute scores evenly between 0 and 1",
    example="""quadrantChart
    title "Reach and engagement of campaigns"
    x-axis "Low Reach" --> "High Reach"
    y-axis "Low Engagement" --> "High Engagement"
    quadrant-1 "We should expand"
    quadrant-2 "Need to promote"
    quadrant-3 "Re-evaluate"
    quadrant-4 "May be improved"
    "Campaign A": [0.3, 0.6]
    "Campaign B": [0.45, 0.23]
    "Campaign C": [0.57, 0.69]
    "Campaign D": [0.78, 0.34]
    "Campaign E": [0.40, 0.34]
    "Campaign F": [0.35, 0.78]
    "Our Target Product": [0.5, 0.6]""",
)

REQUIREMENT_ANALYSIS = ActionNode(
    key="Requirement Analysis",
    expected_type=str,
    instruction="Provide a detailed analysis of the requirements.",
    example="",
)

INCREMENTAL_REQUIREMENT_ANALYSIS = ActionNode(
    key="Incremental Requirement Analysis",
    expected_type=List[str],
    instruction="Propose the comprehensive incremental development requirement analysis on new features and enhanced "
    "features for New Requirements.",
    example=["Require add/update/modify ..."],
)

REFINED_REQUIREMENT_ANALYSIS = ActionNode(
    key="Refined Requirement Analysis",
    expected_type=List[str],
    instruction="Review and refine the existing requirement analysis to align with the evolving needs of the project "
    "due to incremental development. Ensure the analysis comprehensively covers the new features and enhancements "
    "required for the refined project scope.",
    example=["Require add/update/modify ..."],
)

REQUIREMENT_POOL = ActionNode(
    key="Requirement Pool",
    expected_type=List[List[str]],
    instruction="List down the top-5 requirements with their priority (P0, P1, P2).",
    example=[["P0", "The main code ..."], ["P0", "The game algorithm ..."]],
)

REFINED_REQUIREMENT_POOL = ActionNode(
    key="Refined Requirement Pool",
    expected_type=List[List[str]],
    instruction="List no less than 5 requirements with their priority (P0, P1, P2). "
    "Cover both legacy content and incremental content. Retain any content unrelated to incremental development",
    example=[["P0", "The main code ..."], ["P0", "The game algorithm ..."]],
)

UI_DESIGN_DRAFT = ActionNode(
    key="UI Design draft",
    expected_type=str,
    instruction="Provide a simple description of UI elements, functions, style, and layout.",
    example="Basic function description with a simple style and layout.",
)

ANYTHING_UNCLEAR = ActionNode(
    key="Anything UNCLEAR",
    expected_type=str,
    instruction="Mention any aspects of the project that are unclear and try to clarify them.",
    example="",
)

ISSUE_TYPE = ActionNode(
    key="issue_type",
    expected_type=str,
    instruction="Answer BUG/REQUIREMENT. If it is a bugfix, answer BUG, otherwise answer Requirement",
    example="BUG",
)

IS_RELATIVE = ActionNode(
    key="is_relative",
    expected_type=str,
    instruction="Answer YES/NO. If the requirement is related to the old PRD, answer YES, otherwise NO",
    example="YES",
)

REASON = ActionNode(
    key="reason", expected_type=str, instruction="Explain the reasoning process from question to answer", example="..."
)


INCREMENTAL_PRD_CONTEXT = """
Role: You are a professional Product Manager tasked with overseeing incremental development. 
Based on New Requirements, output a New PRD that seamlessly integrates both the Legacy Content and the Incremental Content. Ensure the resulting document captures the complete scope of features, enhancements, and retain content unrelated to incremental development needs for coherence and clarity.

# Context
## New Requirements
{requirements}

## Legacy Content
{old_prd}

## PRD Incremental Content
{prd_increment}
"""

REFINE_PRD_TEMPLATE = """
### New Project Name
{project_name}

### New Requirements
{requirements}

### Legacy Content
{old_prd}

### Search Information
-
"""


NODES = [
    LANGUAGE,
    PROGRAMMING_LANGUAGE,
    ORIGINAL_REQUIREMENTS,
    PROJECT_NAME,
    PRODUCT_GOALS,
    USER_STORIES,
    COMPETITIVE_ANALYSIS,
    COMPETITIVE_QUADRANT_CHART,
    REQUIREMENT_ANALYSIS,
    REQUIREMENT_POOL,
    UI_DESIGN_DRAFT,
    ANYTHING_UNCLEAR,
]

REFINE_NODES = [
    LANGUAGE,
    PROGRAMMING_LANGUAGE,
    REFINED_REQUIREMENTS,
    PROJECT_NAME,
    REFINED_PRODUCT_GOALS,
    REFINED_USER_STORIES,
    COMPETITIVE_ANALYSIS,
    COMPETITIVE_QUADRANT_CHART,
    REFINED_REQUIREMENT_ANALYSIS,
    REFINED_REQUIREMENT_POOL,
    UI_DESIGN_DRAFT,
    ANYTHING_UNCLEAR,
]

INCREMENT_PRD_NODES = [INCREMENTAL_REQUIREMENT_ANALYSIS, REQUIREMENT_POOL]

WRITE_PRD_NODE = ActionNode.from_children("WritePRD", NODES)
REFINE_PRD_NODE = ActionNode.from_children("RefinePRD", REFINE_NODES)
INCREMENTAL_PRD_NODE = ActionNode.from_children("IncrementalPRD", INCREMENT_PRD_NODES)
WP_ISSUE_TYPE_NODE = ActionNode.from_children("WP_ISSUE_TYPE", [ISSUE_TYPE, REASON])
WP_IS_RELATIVE_NODE = ActionNode.from_children("WP_IS_RELATIVE", [IS_RELATIVE, REASON])


def main():
    prompt = WRITE_PRD_NODE.compile(context="")
    logger.info(prompt)
    prompt = REFINE_PRD_NODE.compile(context="")
    logger.info(prompt)


if __name__ == "__main__":
    main()
