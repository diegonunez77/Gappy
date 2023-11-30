import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Assuming you need access to message content for other features
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to scrape the top 10 win rates for a given role
def get_win_rates(role):
    url = f'https://www.op.gg/champions?region=na&tier=emerald_plus&position={role}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.select('tr')[1:11]  # Skip the header row and select the next 10 rows for top 10 champions
        win_rates = []
        for row in rows:
            cells = row.find_all('td')
            name = cells[1].get_text(strip=True)  # Champion name is in the second cell
            win_rate = cells[3].get_text(strip=True)  # Win rate is in the fourth cell
            win_rates.append((name, win_rate))
        return win_rates
    except Exception as e:
        return f'Error retrieving data: {e}'

# Slash command for getting win rates by role
@bot.tree.command(name='wr', description='Get top 10 champion win rates for a specified role')
@app_commands.describe(role='The role to get win rates for')
async def wr(interaction: discord.Interaction, role: str):
    role = role.lower()
    if role not in ['top', 'jungle', 'mid', 'adc', 'support']:
        await interaction.response.send_message('Invalid role. Please choose from top, jungle, mid, adc, support.')
        return
    win_rates = get_win_rates(role)
    if isinstance(win_rates, str):  # If the return is a string, it's an error message
        await interaction.response.send_message(win_rates)
    else:
        response = f'Top 10 {role.title()} Win Rates:\n' + '\n'.join([f'{name}: {rate}' for name, rate in win_rates])
        await interaction.response.send_message(response)

# Function to scrape counters for a given champion and role using Selenium
def get_sorted_counters(champion, role):
    options = Options()
    options.headless = True  # Run in headless mode
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(f'https://www.op.gg/champions/{champion}/counters/{role}?region=na')
        
        # Click the win rate button to sort by ascending win rate
        win_rate_button_selector = 'th.css-1ymfozs.e1tupkk22'  # The selector for the win rate button
        # Wait for the clickable win rate button
        win_rate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, win_rate_button_selector))
        )
        win_rate_button.click()
        # Click again to ensure sorting in ascending order
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, win_rate_button_selector))
        ).click()

        # Wait for the table to be updated after sorting
        WebDriverWait(driver, 10).until(
            EC.staleness_of(win_rate_button)
        )

        # Wait for the rows to be present after sorting
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr[data-champion-key]'))
        )

        # Extract the champion counters
        sorted_counters = []
        for row in rows[-10:]:  # Get the last 10 rows
            try:
                champion_name = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text  # The champion name selector
                win_rate_text = row.find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text.strip('%')  # The win rate selector
                win_rate = float(win_rate_text)
                sorted_counters.append((champion_name, win_rate))
            except Exception as e:
                print(f'Error processing row: {e}')
                continue

        # Sort the list by win rate in ascending order
        sorted_counters.sort(key=lambda x: x[1])

        # Close the driver
        driver.quit()

        # Return the sorted list of counters
        return sorted_counters
    except Exception as e:
        print(f'Encountered an error: {e}')
        driver.quit()
        return f'Error: {e}'



# Slash command for getting counters
@bot.tree.command(name='counters', description='Get sorted counters for a specified champion and role')
@app_commands.describe(champion='The name of the champion', role='The role to get counters for')
async def counters(interaction: discord.Interaction, champion: str, role: str):
    # Defer the response, indicating it's being worked on
    await interaction.response.defer()

    # Fetch the sorted counters
    champion_counters = get_sorted_counters(champion.lower(), role.lower())

    if isinstance(champion_counters, str):  # If the return is a string, it's an error message
        # Follow-up since we deferred the response
        await interaction.followup.send(champion_counters)
    else:
        response_lines = [f'{name}: {rate}%' for name, rate in champion_counters]
        response_message = f'Counters for {champion.title()} in {role.title()} role:\n' + '\n'.join(response_lines)
        # Follow-up since we deferred the response
        await interaction.followup.send(response_message)


# Bot event for when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the slash commands with Discord
    print(f'Logged in as {bot.user}')

# Replace 'YOUR_DISCORD_BOT_TOKEN' with your bot's token
bot.run('MTE3OTIyOTU4MTMxMjUzMjU4MQ.GiVgo3.nU9jmnBKI3Z5jm-EKzzzBMs9o15eJOQYw33z4M')
