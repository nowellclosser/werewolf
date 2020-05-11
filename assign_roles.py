import os
import json
import random
import math

from slack import WebClient

API_TOKEN = os.environ['SLACK_API_TOKEN']

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

# This accessory groups are needed for setting up private channels with the moderator
ALL_SPECIAL_VILLAGERS = STANDARD_SPECIAL_VILLAGERS + ADVANCED_SPECIAL_VILLAGERS
ALL_WEREWOLVES = [WEREWOLF, *SPECIAL_WEREWOLVES]

# Notes for moderator about who has to wake up and things to keep track of?

assert len(ROLE_DESCRIPTIONS) == len(STANDARD_SPECIAL_VILLAGERS) + len(ADVANCED_SPECIAL_VILLAGERS) + len(SPECIAL_WEREWOLVES) + 2

# These are technically not stable, apparently, with a small probability of changing.
VILLAGE_CHANNEL_ID = 'C012NRD42DR'
WEREWOLVES_CHANNEL_ID = 'G012P9CA6RL'
PURGATORY_CHANNEL_ID = 'G012JB44URM'
BOT_MEMBER_ID = 'U012S2HU6H3'


def get_boolean_input(prompt, help_label=None, help_text=None):
    while True:
        options = ' y/n\n' if not (help_label and help_text) else f' y/n/{help_label}\n'
        raw = input(prompt + options).lower()
        if help_label and help_text and raw == help_label:
            print('\n{}\n'.format(help_text))
            continue
        if raw not in {'y', 'n'}:
            print(f"Only 'Y', 'y', 'N', and 'n' and {help_label} are valid inputs. Please try again.")
            continue

        return raw == 'y'


def get_int_input(prompt, lower_bound=0, upper_bound=float('+inf')):
    assert upper_bound >= lower_bound, "Your bounds are not valid"
    while True:
        try:
            result = int(input(prompt + '\n'))
            assert lower_bound <= result <= upper_bound
            return result
        except (AssertionError, ValueError):
            print(f"Couldn't interpret input as an integer between {lower_bound} and {upper_bound}. Please try again.")


def is_bot(client, member_id):
    player_info = client.users_info(user=member_id)
    return player_info.data['user']['is_bot']


def get_display_name(client, member_id):
    player_info = client.users_info(user=member_id)

    display_name = (player_info.data['user']['profile']['display_name']
        or player_info.data['user']['name'])

    return f'@{display_name}'


def find_member_id_by_display_name(client, member):
    members = client.conversations_members(channel=VILLAGE_CHANNEL_ID)

    for member_id in members.data['members']:
        if member_id == BOT_MEMBER_ID:
            continue
        if get_display_name(client, member_id) == member:
            return member_id


# This actually would just need to be a call to conversations.open(), but we
# don't need the im ID for a direct message anyway- just use member ID.
def find_im_by_member_id(client, member_id):
    for im in client.conversations_list(types='im')['channels']:
        if im['user'] == member_id:
            return im['id']

    raise Exception('No IM found for given member id')


def archive_private_channels(client, exceptions=None):
    if not exceptions:
        exceptions = [WEREWOLVES_CHANNEL_ID, PURGATORY_CHANNEL_ID]
    for channel in client.conversations_list(types='private_channel').data['channels']:
        if channel['id'] not in exceptions and not channel['is_archived']:
            # Note that this will stop working November 2020
            client.groups_archive(channel=channel['id'])


def create_or_unarchive_private_channel(client, name, moderator_id):
    name = name.lower().replace(' ', '_')
    # If channel is archived, unarchive it
    for channel in client.conversations_list(types='private_channel').data['channels']:
        if channel['name'] == name:
            if channel['is_archived']:
                client.conversations_unarchive(channel=channel['id'], as_user=True)
                remove_players_from_channel(client, channel['id'], moderator_id)
            return channel['id']

    creation_response = client.conversations_create(
        name=name,
        is_private=True,
    )
    return creation_response['channel']['id']


def remove_players_from_channel(client, channel_id, moderator_id):
    # Add the moderator if they are not already in channel. This prevents
    # the channel from every having only bots in the event of a moderator
    # change.
    try:
        client.conversations_invite(channel=channel_id, users=moderator_id)
    except:
        pass
    members = client.conversations_members(channel=channel_id)

    for member_id in members.data['members']:
        if member_id not in (moderator_id, BOT_MEMBER_ID):
            client.conversations_kick(channel=channel_id, user=member_id)


def main():
    client = WebClient(token=API_TOKEN)

    # Determine which members of the main channel are playing
    print("Welcome to Werewolf!\n")
    print("Let's select the active players. Gathering potential player information from Slack...\n")

    # Set a moderator
    moderator_id = None
    while not moderator_id:
        raw = input("Please give display name of the moderator, including the @, like '@Jane Doe' or '@steve'.\n")
        moderator_id = find_member_id_by_display_name(client, raw)

        if not moderator_id:
            print("That person is not found in the #village channel. Try again.")
            continue

        print(f"Ok, {raw} will be the moderator.\n")

    # Determine which members of the main channel are playing
    active_players = {}
    everyone_playing = get_boolean_input("Is everyone else in the channel playing?")
    player_candidates = client.conversations_members(
        channel=VILLAGE_CHANNEL_ID
    )
    for member_id in player_candidates.data['members']:
        if member_id == moderator_id or is_bot(client, member_id):
            continue

        display_name = get_display_name(client, member_id)
        if everyone_playing or get_boolean_input(f'Is {display_name} playing?'):
            active_players[member_id] = display_name

    # Start configuring roles if there are enough players
    num_players = len(active_players)
    if num_players < 4:
        exit("You do not have enough players, sorry.")

    if get_boolean_input(f"Great. You have {num_players} players. Would you like a summary of all possible roles?"):
        print(json.dumps(ROLE_DESCRIPTIONS, indent=4))

    # Set up werewolves. First pick special ones and then fill in with normal ones up to max allowed
    max_num_wolves = (num_players - 1) // 2
    print(f'Ok, time to configure the werewolves. The absolute maximum number of wolves I will allow is {max_num_wolves}.\n')

    roles = []
    special_werewolves = []
    if get_boolean_input('Would you like to use special werewolves?'):
        for role in SPECIAL_WEREWOLVES:
            if len(special_werewolves) == max_num_wolves:
                print("You have used up all possible wolf slots. Moving on.\n")
                break
            if get_boolean_input(
                    f'Would you like to include the {role}?',
                    help_label='desc',
                    help_text=ROLE_DESCRIPTIONS[role]
            ):
                special_werewolves.append(role)

    roles += special_werewolves
    num_special_wolves = len(special_werewolves)

    num_plain_wolves = 0
    if len(special_werewolves) < max_num_wolves:
        lower_bound = int(not num_special_wolves)
        upper_bound = max_num_wolves - num_special_wolves

        if lower_bound == upper_bound:
            num_plain_wolves = lower_bound
        else:
            num_plain_wolves = get_int_input(
                f'How many normal werewolves (between {lower_bound} and {upper_bound}) would you like in addition to the {num_special_wolves} special one(s)?',
                lower_bound=lower_bound,
                upper_bound=upper_bound
            )

    num_wolves = num_plain_wolves + num_special_wolves
    num_villagers = num_players - num_wolves
    print(f"Ok. You have chosen {num_plain_wolves} plain werewolve(s) and {num_special_wolves} special werewolve(s), leaving {num_villagers} villagers. Let's configure the villagers.\n")

    # Set up the villagers. Pick any special roles you'd like, and then the
    # remaining players will be plain villagers.
    possible_special_villagers = STANDARD_SPECIAL_VILLAGERS
    if get_boolean_input('Would you like to use advanced special villagers?'):
        possible_special_villagers = ALL_SPECIAL_VILLAGERS

    special_villagers = []
    for role in possible_special_villagers:
        if len(special_villagers) < num_villagers:
            if get_boolean_input(
                f'Would you like to include the {role}?',
                help_label='desc',
                help_text=ROLE_DESCRIPTIONS[role]
            ):
                special_villagers.append(role)
        else:
            break

        print(f'{num_villagers - len(special_villagers)} unassigned villagers remaining.\n')

    roles += special_villagers

    if len(special_villagers) == num_villagers:
        print('All available villagers have been made special. Moving on.\n')

    print(f'Ok, you have the following special villager roles: {special_villagers}.\n')

    # Angels and demons?
    print(f'Role selection complete. Reconfiguring Slack and sending roles.')

    # Add the plain roles to fill out the role list and randomly shuffle
    roles += [WEREWOLF] * num_plain_wolves
    roles += [VILLAGER] * (num_players - len(roles))
    random.shuffle(roles)

    # Clear werewolf channel of all but the moderator and the bot
    remove_players_from_channel(client, WEREWOLVES_CHANNEL_ID, moderator_id)

    # Clear purgatory channel of all but the moderator and bot.
    # This channel gives dead players a safe place to comment on the game.
    remove_players_from_channel(client, PURGATORY_CHANNEL_ID, moderator_id)

    # Archive role channels. Below we will unarchive only those needed.
    archive_private_channels(client)

    # Assign shuffled roles to active players, adding to the appropriate
    # private groups and sending them a DM with ther role.
    assigned_roles = {}
    for idx, member_id in enumerate(active_players):
        assigned_role = roles[idx]
        assigned_roles[member_id] = assigned_role
        # summary_text = f'You are in a town of {num_players} members, of which {num_wolves} are werewolves. Everyone else is a villager, including the following special member(s): {special_villagers}.'
        role_text = f'Your role is *{assigned_role}*. {ROLE_DESCRIPTIONS[assigned_role]}'
        player_message = '\n'.join([role_text, 'Good luck!'])

        client.chat_postMessage(
            channel=member_id,
            text=player_message
        )

        # Add werewolves to werewolf channel
        if assigned_role in ALL_WEREWOLVES:
            client.conversations_invite(channel=WEREWOLVES_CHANNEL_ID, users=member_id)

        # Set up a dedicated line to the moderator for any special role.
        if assigned_role in ALL_SPECIAL_VILLAGERS + SPECIAL_WEREWOLVES:
            role_channel_id = create_or_unarchive_private_channel(
                client,
                assigned_role,
                moderator_id
            )
            client.conversations_invite(
                channel=role_channel_id,
                users=','.join([member_id, moderator_id])
            )

    # Send role summary to moderator
    all_roles = '\n'.join([f'<@{mid}>: *{assigned_roles[mid]}*' for mid in active_players])
    client.chat_postMessage(
        channel=moderator_id,
        text=f'All roles:\n {all_roles}'
    )

    # High-level summary sent to village channel
    player_summary = '\n'.join([f'<@{mid}>' for mid in active_players])
    role_summary_header= f'We will begin with *{num_wolves}* werewolve(s) and *{num_villagers}* villagers, including the following special roles:\n'
    special_roles_text = '\n'.join(f'\n_*{role}*_: {ROLE_DESCRIPTIONS[role]}' for role in (special_villagers + special_werewolves)) or 'None!'
    client.chat_postMessage(
        channel=VILLAGE_CHANNEL_ID,
        text=f"Starting a game, moderated by <@{moderator_id}>, with\n\n {player_summary}\n\n {role_summary_header}{special_roles_text}"
    )

if __name__ == '__main__':
    main()


