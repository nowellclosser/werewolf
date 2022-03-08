import os

from slack import WebClient

API_TOKEN = os.environ['SLACK_API_TOKEN']

def main():
    client = WebClient(token=API_TOKEN)
    client.views_publish(
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
                                "text": "See roles",
                                "emoji": True
                            },
                            "value": "see_roles"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Get help",
                                "emoji": True
                            },
                            "value": "help"
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
                                "text": "See current status",
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
