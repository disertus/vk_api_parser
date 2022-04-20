### Collect posts and comments data from VK api

In order to start using the script follow these steps:
1. download all files from this repository, or use the following command in your terminal: `git clone https://github.com/disertus/vk_api_parser`
3. install Python 3 if you are running Windows (python is pre-installed on macOS and Linux) and create a virtual environment by typing in the terminal: `python3 -m venv venv`)
4. activate the virtual environment by typing: `source venv/bin/activate`
5. download and install necessary dependencies by typing: `pip install -r requirements.txt`
6. to launch the program type: `python3 main.py --token "YOUR_ACCESS_TOKEN"` (replace "YOUR_ACCESS_TOKEN" by your actual token)

---

#### Access token
Either a service- or a user-token is needed to be able to interact with VKs API. 
Generate one and pass it as a `--token` argument: 

```python3 main.py --token "906f9719e7b6dc6eb332df85700e635afa6784c7d211a5e3fcc15eb100912a6c8bf6945a8caa86d1034a9"```

`--token` argument is compulsory.

---

#### End date
By default the script covers all the posts starting from current date and till the 19th of Feb 2022 (period preceding the war by several days).
In order to change the end date pass a date of format "YYYY-MM-DD" as `--date` argument: 

`python3 main.py --token "YOUR TOKEN" --date "2022-04-15"`

`--date` argument is optional ("2022-02-19" is passed by default).