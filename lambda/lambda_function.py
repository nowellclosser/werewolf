import json
import urllib.request
import urllib.parse
import os
import base64
import random

import boto3
import slack_sdk

dynamodb = boto3.resource('dynamodb')
slack_client = slack_sdk.WebClient(token=os.environ["BOT_TOKEN"])

WEREWOLF = 'Werewolf'

VILLAGER = 'Villager'
DOCTOR = 'Doctor'
WITCH = 'Witch'
HUNTER ='Hunter'
FORTUNE_TELLER = 'Fortune Teller'

ALPHA_WEREWOLF = 'Alpha Werewolf'
BIG_BAD_WEREWOLF = 'Big Bad Wolf'
BLOCKER_WOLF = 'Blocker Wolf'
CURSED_WOLF_FATHER = 'Cursed Wolf-Father'

ANCIENT = 'Ancient'
ACTOR = 'Actor'
STUTTERING_JUDGE = 'Stuttering Judge'
RAVEN = 'Raven'
SCAPEGOAT = 'Scapegoat'
JAILER = 'Jailer'
GUARDIAN_ANGEL = 'Guardian Angel'
BABYSITTER = 'Babysitter'
BODYGUARD = 'Bodyguard'
VIGILANTE = 'Vigilante'
MILLER = 'Miller' # Penalty to revealing?
PRIEST = 'Priest'
INNOCENT_CHILD = 'Innocent Child'
FRIENDLY_NEIGHBOR = 'Friendly Neighbor'
PROSTITUTE = 'Prostitute'  # Some harm to werewolves as well to balance?
NEAPOLITAN = 'Neapolitan'
FRUIT_VENDOR = 'Fruit Vendor'

# Wild child?
# Ascetic is cool but would need both a werewolf and village ascetic if roles are known
# Two sisters is cool
# Mailman is cool but need one on both sides as well unless roles unkown
# Traitor wolf is interesting but implementation details tricky
# Judas - turns into wolf when dead. if killed at night?
# Bookie - guess who will die the next day for a reward the following night. Kill or investigate?

ROLE_DESCRIPTIONS = {
    WEREWOLF: 'You are a plain werewolf. You will be woken up by the moderator each night with all living werewolves and decide on someone to kill (possibly a werewolf). Your goal is to eliminate all villagers.',

    VILLAGER: 'You are a plain villager, whose only responsibility is to participate in the daily town meeting. Your goal is to eliminate all werewolves.',
    DOCTOR: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person (possibly yourself) to protect. If that person is targeted by the werewolves that night, they will not die. Your goal is to eliminate all werewolves.',
    WITCH: 'You are a villager, but you will be woken up alone by the moderator each night and choose to save someone and/or kill someone. However, you can do each of those only once per game. Your kill cannot be prevented by the doctor.  Your goal is to eliminate all werewolves.',
    HUNTER: 'You are a villager, but whenever you die, whether night or day, you must choose a second person to die with you, with no discussion. Your goal is to eliminate all werewolves.',
    FORTUNE_TELLER: 'You are a villager, but you will be woken up alone by the moderator each night and choose someone to inspect.  The moderator will indicate whether that person is a werewolf. Your goal is to eliminate all werewolves.',

    ANCIENT: 'You are a villager who will not die the first time the werewolves target you.  However, if any villager, like the Witch, kills you, or the townspeople vote to kill you, all villagers lose their powers.',
    ACTOR: 'You are a villager, but the moderator has chosen three other special roles for you, all unknown to you.  Each night, you will be woken up by the moderator and can elect to randomly receive one of those roles, to be used until the following night.  However, a role is used up once you receive it, so you can use your power a maximum of three times.',
    STUTTERING_JUDGE: 'You are a villager. One time during the game at daytime, you may secretly signal to the moderator that a second discussion and vote should be held immediately after the current one, skipping night time.',
    RAVEN: 'You are a villager.  Each night, the moderator will wake you up and ask who you would like to curse with two votes for the following day. You may not curse yourself.  The cursed player does not know they are cursed, and the moderator will also not reveal who was cursed after voting. The moderator WILL of course inform the village when the extra vote makes a difference.',
    SCAPEGOAT: 'You are a villager. In the event that voting ever results in a tie when you are alive, you die and voting for the round ends. However, your revenge, if you die this way, is that you choose someone to not be allowed to vote the following day.',
    JAILER: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person other than yourself to protect. If that person is targeted by the werewolves that night, they will not die. However, if they are a special villager they lose their powers this night.  The moderator must therefore wake you up before any other special villagers.',
    GUARDIAN_ANGEL: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person other than yourself to protect. If that person is targeted by the werewolves that night, they will not die.',
    BABYSITTER: 'You are a villager, but you will be woken up alone by the moderator each night and may pick one person other than yourself to protect. If you choose to protect someone and that person is targeted by the werewolves that night, they will not die. However, if you die that night then your target dies too.',
    BODYGUARD: 'You are a villager, but you will be woken up alone by the moderator each night and may pick one person other than yourself to protect. If you choose to protect someone and that person is targeted by the werewolves that night, you will die instead of them.',
    VIGILANTE: 'You are a villager. You will be woken up alone by the moderator each night to decide whether to kill another player, but you have only two bullets to kill with each game. And if you kill a villager, you yourself will also die from guilt that night.',
    MILLER: 'You are a villager, but you will appear guilty if inspected by a fortune-teller-like role. You have no active special powers.',
    PRIEST: 'You are a villager.  Every time someone dies, you learn whether they were a werewolf or villager.',
    INNOCENT_CHILD: 'You are a villager. At any point during the game you may instruct the moderator to confirm to the group that you are a villager',
    FRIENDLY_NEIGHBOR: 'You are a villager.  Once during the game you may instruct the moderator to tell a second player of your choosing that you are a villager. Please go through the moderator instead of directly messaging the person you choose.',
    PROSTITUTE: 'You are a villager, but every night you are woken up by the moderator and must choose someone to visit. If they have a special role, they lose it for that night. You must be woken up before other special villagers.',
    NEAPOLITAN: 'You are a villager, but you will be woken up alone by the moderator each night and choose someone to inspect.  The moderator will indicate whether that person is a plain villager or not--so you will get the same signal for werewolves and special villagers.',
    FRUIT_VENDOR: 'You are a villager.  Each night, you may instruct the moderator to send someone fruit on your behalf, which does nothing.',

    ALPHA_WEREWOLF: 'You are a werewolf, but you will appear to be a villager if inspected by a fortune-teller-like role.',
    BIG_BAD_WEREWOLF: 'You are a werewolf, but an extremely powerful one.  As long as no werewolves have been eliminated, the moderator will wake you up a second time at night, alone, and you will choose another player to kill. You cannot tell your role to the other werewolves.',
    BLOCKER_WOLF: 'You are a werewolf with an extra ability.  You will be woken up again separately to choose a player to block that night.  If that player is a special villager with night abilities, they will not be able to perform their ability that night.',
    CURSED_WOLF_FATHER: 'You are a werewolf with a special twist. One time during the game, you may secretly signal to the moderator that the target you and the other werewolves picked to kill will become a werewolf instead of dying.  You cannot tell your role to the other werewolves. Finally, note that the fortune teller will receive the updated role if they ask about who was converted the night of conversion.',
}

SHORT_DESCRIPTIONS = {
    WEREWOLF: 'You are a plain werewolf. You will be woken up by the moderator each night with all living werewolves and decide on someone to kill (possibly a werewolf). Your goal is to eliminate all villagers.',

    VILLAGER: 'Plain villager with no powers. The goal is to eliminate all werewolves.',
    DOCTOR: 'Picks one person to protect from the werewolves each night.',
    WITCH: 'Has one kill and one protect to be used at night across the entire game.',
    HUNTER: 'If killed, picks someone to die with them with no discussion.',
    FORTUNE_TELLER: 'Can inspect one person each night to determine whether they are a werewolf.',

    ANCIENT: 'If any villager kills them or the townspeople vote to kill them, all villagers lose their powers.',
    ACTOR: 'Moderator has chosen three special roles for them, all unknown to them. They can choose to receive a random role at night, up to once for each',
    STUTTERING_JUDGE: 'One time during the game at daytime, may signal to the moderator that the following night should be skipped.',
    RAVEN: 'Each night, secretly curses someone else with two votes the following day.',
    SCAPEGOAT: 'If voting ever results in a tie when you are alive, you die and the round ends, and you choose someone to not be allowed to vote the following day.',
    JAILER: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person other than yourself to protect. If that person is targeted by the werewolves that night, they will not die. However, if they are a special villager they lose their powers this night.  The moderator must therefore wake you up before any other special villagers.',
    GUARDIAN_ANGEL: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person other than yourself to protect. If that person is targeted by the werewolves that night, they will not die.',
    BABYSITTER: 'You are a villager, but you will be woken up alone by the moderator each night and may pick one person other than yourself to protect. If you choose to protect someone and that person is targeted by the werewolves that night, they will not die. However, if you die that night then your target dies too.',
    BODYGUARD: 'You are a villager, but you will be woken up alone by the moderator each night and may pick one person other than yourself to protect. If you choose to protect someone and that person is targeted by the werewolves that night, you will die instead of them.',
    VIGILANTE: 'You are a villager. You will be woken up alone by the moderator each night to decide whether to kill another player, but you have only two bullets to kill with each game. And if you kill a villager, you yourself will also die from guilt that night.',
    MILLER: 'You are a villager, but you will appear guilty if inspected by a fortune-teller-like role. You have no active special powers.',
    PRIEST: 'You are a villager.  Every time someone dies, you learn whether they were a werewolf or villager.',
    INNOCENT_CHILD: 'You are a villager. At any point during the game you may instruct the moderator to confirm to the group that you are a villager',
    FRIENDLY_NEIGHBOR: 'You are a villager.  Once during the game you may instruct the moderator to tell a second player of your choosing that you are a villager. Please go through the moderator instead of directly messaging the person you choose.',
    PROSTITUTE: 'You are a villager, but every night you are woken up by the moderator and must choose someone to visit. If they have a special role, they lose it for that night. You must be woken up before other special villagers.',
    NEAPOLITAN: 'You are a villager, but you will be woken up alone by the moderator each night and choose someone to inspect.  The moderator will indicate whether that person is a plain villager or not--so you will get the same signal for werewolves and special villagers.',
    FRUIT_VENDOR: 'You are a villager.  Each night, you may instruct the moderator to send someone fruit on your behalf, which does nothing.',

    ALPHA_WEREWOLF: 'Appears to be a villager if inspected by a fortune-teller-like role.',
    BIG_BAD_WEREWOLF: 'As long as no werewolves have been eliminated, performs a second kill each night.',
    BLOCKER_WOLF: 'Choose a player to block each night, making them temporarily lose special abilities if they have any.',
    CURSED_WOLF_FATHER: 'One time during the game, may convert a werewolf "kill" into another werewolf instead.',
}

STANDARD_SPECIAL_VILLAGERS = [
    DOCTOR,
    WITCH,
    HUNTER,
    FORTUNE_TELLER
]

SPECIAL_WEREWOLVES = [
    ALPHA_WEREWOLF,
    BIG_BAD_WEREWOLF,
    BLOCKER_WOLF,
    CURSED_WOLF_FATHER
]

ADVANCED_SPECIAL_VILLAGERS = [
    ANCIENT,
    ACTOR,
    STUTTERING_JUDGE,
    RAVEN,
    SCAPEGOAT,
    JAILER,
    GUARDIAN_ANGEL,
    BABYSITTER,
    BODYGUARD,
    VIGILANTE,
    MILLER,
    PRIEST,
    INNOCENT_CHILD,
    FRIENDLY_NEIGHBOR,
    PROSTITUTE,
    NEAPOLITAN,
    FRUIT_VENDOR,
]

# These accessory groups are needed for setting up private channels with the moderator
ALL_SPECIAL_VILLAGERS = STANDARD_SPECIAL_VILLAGERS + ADVANCED_SPECIAL_VILLAGERS
ALL_WEREWOLVES = [WEREWOLF, *SPECIAL_WEREWOLVES]

#TODO: Notes for moderator about who has to wake up and things to keep track of

assert len(ROLE_DESCRIPTIONS) == len(STANDARD_SPECIAL_VILLAGERS) + len(ADVANCED_SPECIAL_VILLAGERS) + len(SPECIAL_WEREWOLVES) + 2
assert len(ROLE_DESCRIPTIONS) == len(SHORT_DESCRIPTIONS)

PICK_PLAYERS_TITLE = "Player Configuration"
PICK_PLAYERS_MODAL = {
    "title": {
        "type": "plain_text",
        "text": PICK_PLAYERS_TITLE,
        "emoji": True
    },
    "submit": {
        "type": "plain_text",
        "text": "Submit",
        "emoji": True
    },
    "type": "modal",
    "close": {
        "type": "plain_text",
        "text": "Cancel",
        "emoji": True
    },
    "blocks": [
        {
            "block_id": "moderator_select_block",
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Who will be the moderator?"
            },
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a user",
                    "emoji": True
                },
                "action_id": "select_moderator-action",
            },
        },
        {
            "type": "divider"
        },
        {
            "block_id": "player_select_block",
            "type": "input",
            "element": {
                "type": "multi_users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select users",
                    "emoji": True
                },
                "action_id": "select_players-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Choose at least four additional people to play.",
                "emoji": True
            }
        }
    ]
}

CONFIGURE_WEREWOLVES_TITLE = "Werewolf Configuration"
CONFIGURE_VILLAGERS_TITLE = "Villager Configuration"

WEREWOLF_TABLE_NAME = "WerewolfGame"

WEREWOLF_CHANNEL_PREFIX = 'werewolf_'

#TODO: Won't be able to hardcode these eventually. For channels can go by name and werewolf_X
VILLAGE_CHANNEL_ID = 'C012NRD42DR'
WEREWOLVES_CHANNEL_ID = 'G012P9CA6RL'
PURGATORY_CHANNEL_ID = 'G012JB44URM'
BOT_MEMBER_ID = 'U012S2HU6H3'


def lambda_handler(event, context):
    if event["isBase64Encoded"]:
        event = json.loads(urllib.parse.unquote(base64.b64decode(event['body']).decode("utf-8")).strip('payload='))
        print(event)

    else:
        event = json.loads(event["body"])
        event = event['event']
    if event['type'] == 'block_actions':
        return parse_button_push(event)
    if event['type'] == 'view_submission':
        return parse_view_submission(event)
        

def parse_button_push(event):
    trigger_id = event['trigger_id']
    if event['actions'][0].get('value') == 'start_game':
        slack_client.views_open(
            trigger_id=trigger_id,
            view=json.dumps(PICK_PLAYERS_MODAL)
        )
    
    return {
        'statusCode': 200,
        'body': ''
    }

def parse_view_submission(event):
    # TODO: Validate players are not bots
    if event['view']['title']['text'] == urllib.parse.quote_plus(PICK_PLAYERS_TITLE):
        moderator_id = event['view']['state']['values']['moderator_select_block']['select_moderator-action']['selected_user']
        player_ids = event['view']['state']['values']['player_select_block']['select_players-action']['selected_users']
        if not moderator_id or moderator_id in player_ids or len(player_ids) < 4:
            return {
                "response_action": "push",
                "view": create_validation_error_modal("You must select a moderator, not include them in the players list, and choose at least 4 players.")
            }

        dynamodb.Table(WEREWOLF_TABLE_NAME).put_item(
            Item={
                'ID': event['team']['id'],
                'moderator_id': moderator_id,
                'player_ids': player_ids,
                'game_roles': [],
                'assigned_roles': {}
            }
        )
        return {
            "response_action": "update",
            "view": create_configure_werewolves_modal(len(player_ids))
        }

    if event['view']['title']['text'] == urllib.parse.quote_plus(CONFIGURE_WEREWOLVES_TITLE):
        num_wolves_text = event['view']['state']['values']['werewolf_number_block']['werewolf_number-action']['value']
        special_wolves = event['view']['state']['values']['special_werewolf_block']['special_werewolf-action']['selected_options']
        num_wolves_text_can_be_parsed = True
        try:
            num_wolves = int(num_wolves_text)
        except:
            num_wolves_text_can_be_parsed = False

        current_game_config = dynamodb.Table(WEREWOLF_TABLE_NAME).get_item(Key={'ID': event['team']['id']})['Item']
        num_players = len(current_game_config['player_ids'])

        if len(special_wolves) > num_wolves or not num_wolves_text_can_be_parsed or num_wolves > get_max_num_wolves(num_players) or num_wolves <= 0:
            return {
                "response_action": "push",
                "view": create_validation_error_modal("You either entered an invalid number of werewolves, too high a number of werewolves, or more special werewolves than the total number of werewolves.")
            }

        dynamodb.Table(WEREWOLF_TABLE_NAME).update_item(
            Key={'ID': event['team']['id']},
            UpdateExpression='SET game_roles = :i',
            ExpressionAttributeValues={
                ':i': [urllib.parse.unquote_plus(wolf['text']['text']) for wolf in special_wolves] + [WEREWOLF] * (num_wolves - len(special_wolves))
            }
        )

        return {
            "response_action": "update",
            "view": create_configure_villagers_modal(num_wolves, num_players)
        }

    if event['view']['title']['text'] == urllib.parse.quote_plus(CONFIGURE_VILLAGERS_TITLE):
        current_game_config = dynamodb.Table(WEREWOLF_TABLE_NAME).get_item(Key={'ID': event['team']['id']})['Item']
        special_villagers = event['view']['state']['values']['special_villager_block']['special_villager-action']['selected_options']

        num_players = len(current_game_config['player_ids'])
        num_wolves = len(current_game_config['game_roles'])
        num_villagers = num_players - num_wolves
        num_special_villagers = len(special_villagers)

        if num_special_villagers > num_players - num_wolves:
            return {
                "response_action": "push",
                "view": create_validation_error_modal("You have selected more villager roles than there are villagers.")
            }

        dynamodb.Table(WEREWOLF_TABLE_NAME).update_item(
            Key={'ID': event['team']['id']},
            UpdateExpression='SET game_roles = list_append(game_roles, :i)',
            ExpressionAttributeValues={
                ':i': [urllib.parse.unquote_plus(villager['text']['text']) for villager in special_villagers] + [VILLAGER] * (num_villagers - num_special_villagers)
            }
        )

        assign_roles_and_configure_slack(event['team']['id'])

        return {
            "response_action": "clear"
        }

def archive_private_channels(exceptions=None):
    if not exceptions:
        exceptions = [WEREWOLVES_CHANNEL_ID, PURGATORY_CHANNEL_ID]
    for channel in slack_client.conversations_list(types='private_channel').data['channels']:
        if channel['id'] not in exceptions and not channel['is_archived'] and channel['name'].startswith(WEREWOLF_CHANNEL_PREFIX):
            slack_client.conversations_archive(channel=channel['id'])

def create_channel_name(text):
    return f"{WEREWOLF_CHANNEL_PREFIX}{text.lower().replace(' ', '_')}"


def create_or_unarchive_private_channel(name, moderator_id):
    name = create_channel_name(name)
    # If channel is archived, unarchive it
    for channel in slack_client.conversations_list(types='private_channel').data['channels']:
        if channel['name'] == name:
            if channel['is_archived']:
                slack_client.conversations_unarchive(channel=channel['id'], as_user=True)
                remove_players_from_channel(channel['id'], moderator_id)
            return channel['id']

    creation_response = slack_client.conversations_create(
        name=name,
        is_private=True,
    )
    return creation_response['channel']['id']


def remove_players_from_channel(channel_id, moderator_id):
    # Add the moderator if they are not already in channel. This prevents
    # the channel from every having only bots in the event of a moderator
    # change.
    try:
        slack_client.conversations_invite(channel=channel_id, users=moderator_id)
    except:
        pass
    members = slack_client.conversations_members(channel=channel_id)

    for member_id in members.data['members']:
        #TODO: don't hardcode bot_member_id
        if member_id not in (moderator_id, BOT_MEMBER_ID):
            slack_client.conversations_kick(channel=channel_id, user=member_id)

def assign_roles_and_configure_slack(team_id):
    current_game_config = dynamodb.Table(WEREWOLF_TABLE_NAME).get_item(Key={'ID': team_id})['Item']

    moderator_id = current_game_config['moderator_id']

    # Clear werewolf channel of all but the moderator and the bot
    remove_players_from_channel(WEREWOLVES_CHANNEL_ID, moderator_id)

    # Clear purgatory channel of all but the moderator and bot.
    # This channel gives dead players a safe place to comment on the game.
    remove_players_from_channel(PURGATORY_CHANNEL_ID, moderator_id)

    # Archive role channels. Below we will unarchive only those needed.
    archive_private_channels()

    # Configure village and purgatory channels

    
    
    # randomly assign roles
    game_roles = current_game_config['game_roles']
    random.shuffle(game_roles)

    
    assigned_roles = {}
    for idx, player_id in enumerate(current_game_config['player_ids']):
        assigned_role = game_roles[idx]
        assigned_roles[player_id] = assigned_role

        role_text = f'Your role is *{assigned_role}*. {ROLE_DESCRIPTIONS[assigned_role]}'
        player_message = '\n'.join([role_text, 'Good luck!'])

        slack_client.chat_postMessage(
            channel=player_id,
            text=player_message
        )

        if assigned_role in ALL_WEREWOLVES:
            slack_client.conversations_invite(channel=WEREWOLVES_CHANNEL_ID, users=player_id)

        # Set up a dedicated line to the moderator for any special role.
        if assigned_role in ALL_SPECIAL_VILLAGERS + SPECIAL_WEREWOLVES:
            role_channel_id = create_or_unarchive_private_channel(
                assigned_role,
                moderator_id
            )
            slack_client.conversations_invite(
                channel=role_channel_id,
                users=','.join([player_id, moderator_id])
            )

    active_players = current_game_config['player_ids']

    # Send role summary to moderator
    all_roles = '\n'.join([f'<@{member_id}>: *{assigned_roles[member_id]}*' for member_id in active_players])
    slack_client.chat_postMessage(
        channel=moderator_id,
        text=f'All roles:\n {all_roles}'
    )

    # High-level summary sent to village channel
    num_wolves = 0
    special_characters = set()
    for player_id, role in assigned_roles.items():
        if role in ALL_WEREWOLVES:
            num_wolves += 1
        if role in SPECIAL_WEREWOLVES + ALL_SPECIAL_VILLAGERS:
            special_characters.add(role)
    num_villagers = len(active_players) - num_wolves
    player_summary = '\n'.join([f'<@{mid}>' for mid in active_players])
    role_summary_header= f'We will begin with *{num_wolves}* werewolve(s) and *{num_villagers}* villagers, including the following special roles:\n'
    special_roles_text = '\n'.join(f'\n_*{role}*_: {ROLE_DESCRIPTIONS[role]}' for role in (special_characters)) or 'None!'
    slack_client.chat_postMessage(
        channel=VILLAGE_CHANNEL_ID,
        text=f"Starting a game, moderated by <@{moderator_id}>, with\n\n {player_summary}\n\n {role_summary_header}{special_roles_text}"
    )

    dynamodb.Table(WEREWOLF_TABLE_NAME).update_item(
        Key={'ID': team_id},
        UpdateExpression='SET assigned_roles = :i',
        ExpressionAttributeValues={
            ':i': assigned_roles
        }
    )
    print("Made it to end of role assignment")


def get_max_num_wolves(num_players):
    return (num_players - 1) // 2


def create_configure_werewolves_modal(num_players):
    return {
        "title": {
            "type": "plain_text",
            "text": CONFIGURE_WEREWOLVES_TITLE,
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "type": "modal",
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"Ok, the number of players is {num_players}. Let's configure the werewolves. We will allow up to {get_max_num_wolves(num_players)}. How many would you like?",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "werewolf_number_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "werewolf_number-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": " ",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "block_id": "special_werewolf_block",
                "text": {
                    "type": "mrkdwn",
                    "text": "If you would like to include any special werewolves, please select each here. We will subtract the number selected here from the total number of werewolves given above and make the remaining number of standard werewolves."
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": f"{role}"
                            },
                            "description": {
                                "type": "plain_text",
                                "text": f"{SHORT_DESCRIPTIONS[role]}"
                            },
                            "value": role
                        } for role in SPECIAL_WEREWOLVES
                    ],
                    "action_id": "special_werewolf-action",
                }
            }
        ]
    }


def create_configure_villagers_modal(num_wolves, num_players):
    return {
        "title": {
            "type": "plain_text",
            "text": CONFIGURE_VILLAGERS_TITLE,
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "type": "modal",
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "block_id": "special_villager_block",
                "text": {
                    "type": "mrkdwn",
                    "text": f"The number of werewolves is {num_wolves}, so the remaining number of villagers is {num_players - num_wolves}. Let's pick their roles.  Choose up to {num_players - num_wolves} special role(s) below and then the remaining player(s) will be plain villagers.",
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": f"{role}"
                            },
                            "description": {
                                "type": "plain_text",
                                "text": f"{SHORT_DESCRIPTIONS[role]}"
                            },
                            "value": role
                        } for role in STANDARD_SPECIAL_VILLAGERS
                    ],
                    "action_id": "special_villager-action",
                }
            }
        ]
    }


# TODO: Use errors functionality
def create_validation_error_modal(error_message):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Validation Error",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Go Back",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"{error_message}",
                    "emoji": True
                }
            }
        ]
    }
