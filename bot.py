import logging
import random, re
import configuration

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = ''

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



praises = []
submission_praises = []
file_path = configuration.FILE_DIRECTORY_PATH
accept_suggestions = True

format_praises_header = "Список фраз в боте:\nДля управления используйте индексы в начале строки.\n\n"
format_suggestions_header = "Список фраз в предложке:\nДля управления используйте индексы в начале строки.\n\n"
access_denied = "У вас нету доступа к этой команде"
help_manage = "placeholder help"
help_manage_suggestions = "/manage suggestions:\n/manage suggestions show - вывести список всех фраз, в основном списке и в предложке\n/manage suggestions add <index> - добавить фразу из предложки в список основных\n/manage suggestions remove <index>  - убрать фразу из предложки"
help_manage_suggestions_add = "placeholder help with adding suggestions"
help_manage_suggestions_remove = "placeholder help with adding suggestions"
help_manage_praises = "/manage praises:\n/manage praises show - вывести список всех фраз, в основном списке и в предложке\n/manage praises remove <index>  - убрать фразу из основного списка"
help_manage_praises_remove = "/manage praises remove <index>  - убрать фразу из основного списка"
help_suggest = "/suggest \"<phrase>\" - добавить фразу в предложку. Фраза обязательно должна быть в ковычках."
start_welcome_text = "Привет! Я бот похвалы.\nЧтобы получить комплимент, напиши \"/praise\" или \"похвали меня\""
bot_unrecognized_command = "Нераспознанная команда"

def check_credentials(user_id):
    for staff_id in configuration.staff.keys():
        if staff_id == str(user_id):
            return True
            
    return False

def parse_praises():
    with open(file_path + "praises.txt", encoding="utf8") as f:
        lines = f.readlines()

    for line in lines:
        praises.append(line[:-1])

parse_praises()


def parse_praise_suggestions():
    with open(file_path + "suggestions.txt", encoding="utf8") as f:
        lines = f.readlines()

    for line in lines:
        submission_praises.append(line[:-1])

parse_praise_suggestions()


def return_praise():
    praise_text = praises[random.randint(0, len(praises)-1)]
    return praise_text



def format_praises(list):
    formatted_list = format_praises_header
    index = 0

    for phrase in list:
        formatted_list += f"{index}: \"{phrase}\",\n"
        index += 1

    return formatted_list

def format_suggestions(list):
    formatted_list = format_suggestions_header
    index = 0

    for phrase in list:
        formatted_list += f"{index}: \"{phrase}\",\n"
        index += 1

    return formatted_list

def add_praise(message):
    praise_text = re.search("\"(.*?)\"", message).group(1)

    if accept_suggestions:

        if praise_text not in submission_praises and praise_text not in praises:
            submission_praises.append(praise_text)

            with open(file_path + "suggestions.txt", "a", encoding="utf8") as f:
                f.write(praise_text + "\n")

            return f"Фраза \"{praise_text}\" добавлена в список на добавление"


        else:
            return f"Фраза \"{praise_text}\" уже есть в списке"



def accept_praise(message_text):
    phrase_index = int(re.search("([0-9]+)", message_text).group(1))

    phrase = submission_praises[phrase_index]

    praises.append(phrase)
    submission_praises.remove(phrase)

    with open(file_path + "praises.txt", "a", encoding="utf8") as f:
        f.write(phrase + "\n")

    with open(file_path + "suggestions.txt", "r", encoding="utf8") as f:
        lines = f.readlines()

    with open(file_path + "suggestions.txt", "w", encoding="utf8") as f:
        for line in lines:
            if line.strip("\n") != phrase:
                f.write(line)

    return f"Фраза \"{phrase}\" успешно добавлена в список общих фраз!"



def deny_praise(message_text):
    phrase_index = int(re.search("([0-9]+)", message_text).group(1))

    phrase = submission_praises[phrase_index]

    submission_praises.remove(phrase)

    with open(file_path + "suggestions.txt", "r", encoding="utf8") as f:
        lines = f.readlines()

    with open(file_path + "suggestions.txt", "w", encoding="utf8") as f:
        for line in lines:
            if line.strip("\n") != phrase:
                f.write(line)

    return f"Фраза \"{phrase}\" успешно удалена."


def remove_praise(message_text):
    phrase_index = int(re.search("([0-9]+)", message_text).group(1))

    phrase = praises[phrase_index]

    praises.remove(phrase)

    with open(file_path + "praises.txt", "r", encoding="utf8") as f:
        lines = f.readlines()

    with open(file_path + "praises.txt", "w", encoding="utf8") as f:
        for line in lines:
            if line.strip("\n") != phrase:
                f.write(line)

    return f"Фраза \"{phrase}\" успешно удалена."


def unrecognized_command(text):
    return "Нераспознанная команда \"" + text + "\""



def debug(user_id):
    return check_credentials(user_id)





@dp.message_handler(commands=['suggest'])
async def suggest_phrase(message: types.Message):
    user_id = message.from_user.id
    isStaff = check_credentials(user_id)

    if isStaff:

        if len(message.text.split(" ")) == 2:
            await message.answer(add_praise(message.text))
        else: 
            await message.answer(help_suggest)
    else:
        await message.answer(access_denied)



@dp.message_handler(commands=['manage'])
async def manage_bot(message: types.Message):
    user_id = message.from_user.id
    msg = message.text.lower()
    isStaff = check_credentials(user_id)

    if isStaff:
        args = msg.split(" ")
        if len(args) == 4:
            match = re.search("([0-9]+)", args[3])

        if len(args) <= 1:
            await message.answer(help_manage)


        elif args[1] == "suggestions":
            if len(args) <= 2:
                await message.answer(help_manage_suggestions)

            elif args[2] == "show":
                await message.answer(format_praises(praises) + "\n\n" + format_suggestions(submission_praises))

            elif args[2] == "add":
                if len(args) <= 3:
                    await message.answer(help_manage_suggestions_add)

                elif match:
                    await message.answer(accept_praise(message.text))

                else: 
                    await message.answer(help_manage_suggestions_add)
            

            elif args[2] == "remove":
                if len(args) <= 3:
                    await message.answer(help_manage_suggestions_remove)

                elif match:
                    await message.answer(deny_praise(message.text))

                else: 
                    await message.answer(help_manage_suggestions_remove)

            else:
                await message.answer(help_manage_suggestions)

        elif args[1] == "praises":
            if len(args) <= 2:
                await message.answer(help_manage_praises)

            elif args[2] == "show":
                await message.answer(format_praises(praises) + "\n\n" + format_suggestions(submission_praises))

            elif args[2] == "remove":
                if len(args) <= 3:
                    await message.answer(help_manage_praises_remove)

                elif match:
                    await message.answer(remove_praise(message.text))

                else: 
                    await message.answer(help_manage_praises_remove)

        else:
            await message.answer(str(args))

    else:
        await message.answer(access_denied)







@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

    """
    This handler will be called when user sends `/start` or `/help` command
    """

    
    await message.reply(start_welcome_text) 


@dp.message_handler(commands=['praise'])
async def praise(message: types.Message):
    user_id = message.from_user.id
    print(f"praise request issued by {user_id}")
    await message.answer(return_praise())


@dp.message_handler(commands=['debug'])
async def debug_bot(message: types.Message):
    user_id = message.from_user.id
    await message.answer(debug(user_id))

@dp.message_handler()
async def process_non_command_message(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    msg = message.text.lower()
    user_id = message.from_user.id
    isStaff = check_credentials(user_id)

    unrecognized_command = bot_unrecognized_command + f" \"{message.text}\""
    
    if "похвали меня" in msg:
        print(f"praise request issued by {user_id}")
        await message.answer(return_praise())

    else:
        print(f"unrecognized command issued by {user_id}")
        await message.answer(unrecognized_command)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)