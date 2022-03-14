import os

import slack_sdk

def main():
    slack_sdk.WebClient(token=os.environ["SLACK_API_TOKEN"]).views_publish(
        user_id='U012M822WGM',
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome to Werewolf Home!"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "What would you like to do?",
                        "emoji": True
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Start a new game",
                                "emoji": True
                            },
                            "style": "primary",
                            "value": "start_game"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "See alive players",
                                "emoji": True
                            },
                            "value": "see_alive_players"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "See possible roles",
                                "emoji": True
                            },
                            "value": "see_roles"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "See game rules",
                                "emoji": True
                            },
                            "value": "see_rules"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "If you are currently moderating a game, you may use the following:",
                        "emoji": True
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Begin night",
                                "emoji": True
                            },
                            "style": "primary",
                            "value": "begin_night"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Call for vote",
                                "emoji": True
                            },
                            "style": "primary",
                            "value": "call_vote"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "End vote",
                                "emoji": True
                            },
                            "style": "primary",
                            "value": "end_vote"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "See game status",
                                "emoji": True
                            },
                            "value": "see_status"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Kill a player",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": "kill_player"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Undo a kill",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": "undo_kill_player"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "End game",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": "end_game"
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
        }
    )

if __name__ == '__main__':
    main()
