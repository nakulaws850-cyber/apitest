import os
import json
import time
import random
import asyncio
import traceback
import requests
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8943649009:AAEhOrtNlhwiDt1RsUIE6duWQ7N25oExf-M"
API_KEY = "vipxw5wpHkI0P0qWg96QR9EP69uTROjR"
API_URL = "https://vipytapi.site/download"

DB_FILE = "sent_songs.json"
MAX_DURATION = 1200   # 20 minutes
MIN_DURATION = 30     # 30 seconds
AUTO_INTERVAL = 10    # seconds

# --- BATCHING CONFIG ---
BATCH_MIN = 1
BATCH_MAX = 5
BATCH_DELAY_MIN = 0.5
BATCH_DELAY_MAX = 2.0

# --- SEARCH QUERIES (250+) ---
SEARCH_QUERIES = [
    # ---------- Hindi / Bollywood ----------
    "hindi song", "bollywood song", "hindi hit song", "bollywood hit song",
    "hindi romantic song", "hindi sad song", "hindi party song",
    "hindi old song", "old hindi song", "90s hindi song", "80s hindi song",
    "70s hindi song", "60s hindi song", "hindi melody song", "hindi love song",
    "hindi new song 2024", "hindi new song 2025", "hindi new song 2026",
    "bollywood romantic song", "bollywood sad song", "bollywood dance song",
    "bollywood item song", "bollywood classic song", "bollywood evergreen song",
    "bollywood mashup", "bollywood remix", "bollywood lofi",
    "hindi lofi song", "hindi chill song", "hindi workout song",

    # ---------- Punjabi ----------
    "punjabi song", "punjabi hit song", "punjabi romantic song",
    "punjabi sad song", "punjabi new song", "punjabi old song",
    "punjabi party song", "punjabi bhangra song", "punjabi folk song",
    "diljit dosanjh song", "sidhu moose wala song", "karan aujla song",
    "ap dhillon song", "guru randhawa song", "ammy virk song",
    "b praak song", "jassie gill song", "harrdy sandhu song",
    "parmish verma song", "amrit maan song", "g sidhu song",
    "shubh song", "cheema y song", "gur sidhu song",
    "punjabi lofi song", "punjabi remix song", "punjabi dj song",
    "punjabi sad song 2024", "punjabi love song", "punjabi breakup song",
    "punjabi jatt song", "punjabi suit song", "punjabi gabru song",
    "punjabi female song", "punjabi duet song", "punjabi folk boliyaan",

    # ---------- Bhojpuri ----------
    "bhojpuri song", "bhojpuri hit song", "bhojpuri new song",
    "bhojpuri dance song", "bhojpuri romantic song", "bhojpuri sad song",
    "khesari lal song", "pawan singh song", "nirahua song",
    "bhojpuri gana", "bhojpuri video song", "bhojpuri item song",
    "bhojpuri folk song", "bhojpuri birha", "bhojpuri kajri",
    "bhojpuri new song 2024", "bhojpuri new song 2025",
    "bhojpuri dj song", "bhojpuri remix song", "bhojpuri lofi song",
    "bhojpuri love song", "bhojpuri hit gana", "bhojpuri trend song",
    "bhojpuri viral song", "bhojpuri chaita", "bhojpuri sohar",
    "bhojpuri jhumar", "bhojpuri chhath geet", "bhojpuri vivah geet",
    "ravi kishan song", "shilpi raj song", "neelkamal singh song",
    "ankush raja song", "ritu pathak song", "shubham singh song",
    "bhojpuri album song", "bhojpuri top song", "bhojpuri chartbuster",

    # ---------- Singer Specific ----------
    "arijit singh song", "atif aslam song", "sonu nigam song",
    "kishore kumar song", "lata mangeshkar song", "udit narayan song",
    "shreya ghoshal song", "neha kakkar song", "alka yagnik song",
    "kumar sanu song", "asha bhosle song", "mohammed rafi song",
    "mukesh song", "jagjit singh ghazal", "armaan malik song",
    "jubin nautiyal song", "darshan raval song", "sachet parampara song",
    "atif aslam romantic song", "shreya ghoshal romantic song",
    "sonu nigam sad song", "kishore kumar romantic song",
    "lata mangeshkar bhajan", "arijit singh sad song",
    "arijit singh romantic song", "jubin nautiyal romantic song",
    "arijit singh new song", "arijit singh hit song", "arijit singh lofi",
    "atif aslam sad song", "atif aslam new song", "atif aslam hit song",
    "sonu nigam romantic song", "sonu nigam hit song",
    "udit narayan romantic song", "kumar sanu romantic song",
    "kumar sanu sad song", "alka yagnik romantic song",
    "shreya ghoshal sad song", "neha kakkar romantic song",
    "neha kakkar party song", "honey singh song", "badshah song",
    "yo yo honey singh song", "raftaar song", "divine song",
    "emiway bantai song", "mc stan song", "king song",
    "talha anjum song", "talhah yunus song", "young stunners song",

    # ---------- Mood Based ----------
    "breakup song", "love song hindi", "dance song hindi",
    "emotional song hindi", "friendship song hindi",
    "sad song hindi", "evergreen hindi song", "romantic hits",
    "heartbreak song hindi", "motivational song hindi",
    "study song hindi", "sleep song hindi", "chill hindi song",
    "relaxing hindi song", "travel song hindi", "road trip song hindi",
    "party song hindi", "wedding song hindi", "sangeet song hindi",
    "hindi lofi sad song", "hindi lofi romantic song", "hindi lofi chill",
    "hindi gym song", "hindi workout motivation song", "hindi energy song",
    "hindi morning song", "hindi evening song", "hindi night song",
    "hindi rain song", "hindi monsoon song", "hindi winter song",
    "hindi summer song", "hindi happy song", "hindi joyful song",
    "hindi crying song", "hindi alone song", "hindi lonely song",
    "hindi miss you song", "hindi pyar song", "hindi dosti song",
    "hindi yaad song", "hindi judai song", "hindi intezaar song",

    # ---------- Regional ----------
    "haryanvi song", "rajasthani song", "marathi song",
    "tamil song", "telugu song", "kannada song", "malayalam song",
    "assamese song", "bengali song", "gujarati song",
    "odia song", "urdu song", "nepali song",
    "haryanvi new song", "marathi romantic song", "tamil hit song",
    "telugu hit song", "bengali romantic song", "gujarati garba song",
    "rajasthani folk song", "assamese bihu song", "odia bhajan",
    "kannada romantic song", "malayalam melody song",
    "haryanvi dj song", "haryanvi dance song", "haryanvi folk song",
    "sapna chaudhary song", "gulzaar chhaniwala song", "bjp haryanvi song",
    "marathi new song", "marathi dj song", "marathi lavani song",
    "marathi bhajan", "marathi powada", "marathi natya geet",
    "tamil new song", "tamil romantic song", "tamil sad song",
    "tamil kuthu song", "tamil melody song", "tamil folk song",
    "anirudh song", "ar rahman song", "ilayaraja song",
    "yuvan shankar raja song", "gv prakash song", "sid sriram song",
    "telugu new song", "telugu romantic song", "telugu mass song",
    "telugu folk song", "telugu melody song", "devi sri prasad song",
    "thaman song", "ss thaman song", "dsp song",
    "kannada new song", "kannada hit song", "kannada folk song",
    "kannada melody song", "vijay prakash song", "raghu dixit song",
    "malayalam new song", "malayalam hit song", "malayalam melody song",
    "malayalam folk song", "malayalam romantic song",
    "bengali new song", "bengali hit song", "bengali folk song",
    "bengali baul song", "bengali rabindra sangeet", "bengali nazrul geeti",
    "gujarati new song", "gujarati garba", "gujarati dandiya song",
    "gujarati folk song", "gujarati bhajan", "gujarati lokgeet",
    "odia new song", "odia hit song", "odia folk song",
    "odia romantic song", "odia bhajan", "odia sambalpuri song",
    "assamese new song", "assamese bihu geet", "assamese folk song",
    "assamese modern song", "assamese borgeet", "assamese lokgeet",
    "nepali new song", "nepali hit song", "nepali romantic song",
    "nepali sad song", "nepali folk song", "nepali lok geet",
    "urdu ghazal", "urdu nazm", "urdu poetry song",
    "kashmiri song", "sindhi song", "konkani song", "tulu song",
    "maithili song", "magahi song", "chhattisgarhi song",
    "garhwali song", "kumaoni song", "dogri song",

    # ---------- Devotional / Classical / Bhajan ----------
    "indian classical song", "sufi song", "qawwali song",
    "bhajan song", "devotional song hindi", "hanuman bhajan",
    "shiv bhajan", "krishna bhajan", "gurbani shabad",
    "durga bhajan", "ganesh bhajan", "lakshmi bhajan",
    "sai baba bhajan", "radha krishna bhajan", "ram bhajan",
    "shirdi sai bhajan", "mata bhajan", "navratri bhajan",
    
    # --- Krishna Bhajan ---
    "krishna bhajan", "krishna bhajan hindi", "krishna bhajan new",
    "krishna bhajan 2024", "krishna bhajan 2025",
    "radha krishna bhajan", "radha krishna song", "radha bhajan",
    "vrindavan bhajan", "vrindavan kirtan", "iskcon kirtan",
    "iskcon bhajan", "hare krishna kirtan", "hare rama hare krishna",
    "krishna flute song", "krishna flute instrumental", "krishna janmashtami song",
    "janmashtami bhajan", "janmashtami special song", "janmashtami kirtan",
    "banke bihari bhajan", "banke bihari song", "radha rani bhajan",
    "radha rani song", "barsana bhajan", "govind bhajan",
    "madhuri bhajan", "krishna janam bhajan", "krishna leela song",
    "krishna bhajan by anuradha paudwal", "krishna bhajan by jubin nautiyal",
    "krishna bhajan by arijit singh", "krishna bhajan by shreya ghoshal",
    "krishna bhajan by sonu nigam", "krishna bhajan by lata mangeshkar",
    
    # --- Hanuman Bhajan ---
    "hanuman bhajan", "hanuman bhajan new", "hanuman bhajan 2024",
    "hanuman bhajan 2025", "hanuman chalisa", "hanuman chalisa fast",
    "hanuman chalisa slow", "hanuman chalisa 108 times",
    "hanuman chalisa by gulshan kumar", "hanuman chalisa by hariharan",
    "hanuman chalisa by shankar mahadevan", "hanuman chalisa by amitabh bachchan",
    "hanuman ashtak", "hanuman stuti", "hanuman aarti",
    "hanuman mantra", "hanuman mantra 108 times", "hanuman naam",
    "bajrangbali bhajan", "bajrangbali song", "bajrangbali chalisa",
    "hanuman ji bhajan", "hanuman ji song", "hanuman ji ki aarti",
    "sankat mochan hanuman", "sankat mochan bhajan", "sankat mochan hanuman ashtak",
    "hanuman bhajan by anuradha paudwal", "hanuman bhajan by narendra chanchal",
    "hanuman bhajan by gulshan kumar", "hanuman bhajan by hari om sharan",
    "mangal murti maruti nandan", "jai hanuman gyan gun sagar",
    
    # --- Ram Bhajan ---
    "ram bhajan", "ram bhajan new", "ram bhajan 2024", "ram bhajan 2025",
    "ram bhajan hindi", "ram katha", "ram kirtan",
    "ram naam", "ram naam 108 times", "ram ram jap",
    "ram aarti", "ram ji ki aarti", "ram stuti", "ram chalisa",
    "ram raksha stotra", "ram raksha", "ram raksha path",
    "sundarkand", "sundarkand path", "sundarkand full",
    "sundarkand by gulshan kumar", "sundarkand by hariharan",
    "ramayan bhajan", "ramayan song", "ramayan chaupai",
    "ram bhajan by anuradha paudwal", "ram bhajan by narendra chanchal",
    "ram bhajan by gulshan kumar", "ram bhajan by hari om sharan",
    "siya ram bhajan", "sita ram bhajan", "sita ram song",
    "jai shree ram song", "jai shree ram bhajan", "jai shree ram mantra",
    "ayodhya ram bhajan", "ayodhya ram song", "ayodhya ram mandir song",
    "ram mandir bhajan", "ram mandir song", "ram lalla song",
    "ram lalla bhajan", "ram lalla darshan song",
    "shri ram chandra kripalu", "shri ram jai ram jai jai ram",
    "raghupati raghav raja ram", "thumak chalata ramchandra",
    "mangal bhavan amangal hari", "ram siya ram song",
    
    # --- Shiv Bhajan ---
    "shiv bhajan", "shiv bhajan new", "shiv bhajan 2024", "shiv bhajan 2025",
    "shiv bhajan hindi", "shiv kirtan", "shiv naam",
    "shiv aarti", "shiv ji ki aarti", "shiv chalisa", "shiv stuti",
    "shiv mantra", "shiv mantra 108 times", "mahamrityunjay mantra",
    "mahamrityunjay mantra 108 times", "mahamrityunjay jaap",
    "om namah shivaya", "om namah shivaya 108 times", "om namah shivaya chant",
    "shiv tandav stotram", "shiv tandav", "shiv tandav by shankar mahadevan",
    "rudrashtakam", "rudrashtakam by gulshan kumar", "shiv puran",
    "shiv bhajan by anuradha paudwal", "shiv bhajan by narendra chanchal",
    "shiv bhajan by gulshan kumar", "shiv bhajan by hari om sharan",
    "bholenath bhajan", "bholenath song", "bholenath kirtan",
    "mahadev bhajan", "mahadev song", "mahadev kirtan",
    "shiv parvati bhajan", "shiv parvati song", "shiv vivah song",
    "shivratri bhajan", "shivratri song", "shivratri special bhajan",
    "shivratri kirtan", "mahashivratri bhajan", "mahashivratri song",
    "somvar bhajan", "somvar vrat katha", "shiv somvar bhajan",
    "kailash ke nivasi", "jai shiv shankar", "har har mahadev",
    "bam bam bhole", "bhole ki jai", "shiv shambhu",
    
    # --- Durga / Kali Mata Bhajan ---
    "durga bhajan", "durga bhajan new", "durga bhajan 2024", "durga bhajan 2025",
    "durga bhajan hindi", "durga kirtan", "durga naam",
    "durga aarti", "durga ji ki aarti", "durga chalisa", "durga stuti",
    "durga mantra", "durga mantra 108 times", "durga saptashati",
    "durga saptashati path", "durga saptashati full",
    "durga bhajan by anuradha paudwal", "durga bhajan by narendra chanchal",
    "durga bhajan by gulshan kumar", "durga bhajan by hari om sharan",
    "mata bhajan", "mata bhajan new", "mata ki aarti", "mata chalisa",
    "mata rani bhajan", "mata rani song", "mata rani kirtan",
    "kali mata bhajan", "kali mata song", "kali mata kirtan",
    "kali mata aarti", "kali mata chalisa", "kali mata mantra",
    "kali bhajan", "kali song", "kali kirtan", "kali aarti",
    "maa kali bhajan", "maa kali song", "maa kali kirtan",
    "jai mata di", "jai mata di song", "jai mata di bhajan",
    "navratri bhajan", "navratri song", "navratri kirtan",
    "navratri special bhajan", "navratri special song", "navratri garba",
    "navratri aarti", "navratri mata bhajan", "navratri 2024 bhajan",
    "navratri 2025 bhajan", "navratri day 1 bhajan", "navratri day 2 bhajan",
    "navratri day 3 bhajan", "navratri day 4 bhajan", "navratri day 5 bhajan",
    "navratri day 6 bhajan", "navratri day 7 bhajan", "navratri day 8 bhajan",
    "navratri day 9 bhajan", "navratri colors song", "navratri dj song",
    "navratri garba song", "navratri dandiya song", "navratri nonstop garba",
    "sherawali bhajan", "sherawali mata bhajan", "sherawali song",
    "vaishno devi bhajan", "vaishno devi song", "vaishno devi aarti",
    "vaishno devi chalisa", "jai vaishno devi", "vaishno devi kirtan",
    "chamunda bhajan", "chamunda song", "chamunda aarti",
    "ambey mata bhajan", "ambey mata song", "ambey mata aarti",
    "ambey bhajan", "ambey song", "ambey kirtan",
    "durga chalisa by gulshan kumar", "durga chalisa by anuradha paudwal",
    "jai ambe gauri", "jai ambe gauri aarti", "ambe tu hai jagdambe kali",
    "durga hai meri mata", "mata ke charno mein", "mata rani ke bhajan",
    
    # --- Lakshmi Bhajan ---
    "lakshmi bhajan", "lakshmi bhajan new", "lakshmi bhajan 2024",
    "lakshmi bhajan 2025", "lakshmi aarti", "lakshmi ji ki aarti",
    "lakshmi chalisa", "lakshmi stuti", "lakshmi mantra",
    "lakshmi mantra 108 times", "lakshmi sukta", "lakshmi kirtan",
    "lakshmi bhajan by anuradha paudwal", "lakshmi bhajan by gulshan kumar",
    "lakshmi bhajan by hari om sharan", "lakshmi bhajan by narendra chanchal",
    "diwali bhajan", "diwali song", "diwali aarti", "diwali laxmi puja",
    "diwali special bhajan", "diwali special song", "diwali kirtan",
    "laxmi mata bhajan", "laxmi mata song", "laxmi mata aarti",
    "laxmi mata chalisa", "laxmi mata kirtan", "laxmi mata mantra",
    "mahalakshmi bhajan", "mahalakshmi song", "mahalakshmi aarti",
    "mahalakshmi chalisa", "mahalakshmi mantra", "mahalakshmi kirtan",
    "om jai lakshmi mata", "om jai lakshmi mata aarti",
    "jai lakshmi ramna", "lakshmi ramna song",
    "kanakadhara stotram", "kanakadhara stotram by ms subbulakshmi",
    "shree sukta", "shree sukta path", "shree yantra mantra",
    "kuber bhajan", "kuber song", "kuber mantra", "kuber aarti",
    "dhan laxmi bhajan", "dhan laxmi song", "dhan laxmi mantra",
    
    # --- Ganesh Bhajan ---
    "ganesh bhajan", "ganesh bhajan new", "ganesh bhajan 2024",
    "ganesh bhajan 2025", "ganesh aarti", "ganesh ji ki aarti",
    "ganesh chalisa", "ganesh stuti", "ganesh mantra",
    "ganesh mantra 108 times", "ganesh kirtan", "ganesh vandana",
    "ganesh bhajan by anuradha paudwal", "ganesh bhajan by gulshan kumar",
    "ganesh bhajan by narendra chanchal", "ganesh bhajan by hari om sharan",
    "ganpati bhajan", "ganpati song", "ganpati aarti", "ganpati kirtan",
    "ganpati bappa song", "ganpati bappa bhajan", "ganpati bappa morya",
    "ganesh chaturthi bhajan", "ganesh chaturthi song", "ganesh chaturthi aarti",
    "ganesh chaturthi kirtan", "ganesh chaturthi special",
    "ganesh visarjan song", "ganesh visarjan bhajan", "ganesh visarjan aarti",
    "siddhivinayak bhajan", "siddhivinayak song", "siddhivinayak aarti",
    "siddhivinayak chalisa", "siddhivinayak mantra", "siddhivinayak kirtan",
    "vakratunda mahakaya", "vakratunda mantra", "vakratunda shloka",
    "om gam ganpataye namah", "om gam ganpataye namah 108 times",
    "jai ganesh jai ganesh", "jai ganesh jai ganesh aarti",
    "sukhkarta dukhharta", "sukhkarta dukhharta aarti",
    "mangalmurti morya", "mangalmurti morya aarti",
    "ganpati bappa morya song", "ganpati bappa morya bhajan",
    
    # --- Sai Baba Bhajan ---
    "sai baba bhajan", "sai baba bhajan new", "sai baba bhajan 2024",
    "sai baba bhajan 2025", "sai baba aarti", "sai baba kirtan",
    "sai baba chalisa", "sai baba mantra", "sai baba stuti",
    "sai baba bhajan by anuradha paudwal", "sai baba bhajan by gulshan kumar",
    "sai baba bhajan by narendra chanchal", "sai baba bhajan by hari om sharan",
    "shirdi sai bhajan", "shirdi sai song", "shirdi sai aarti",
    "shirdi sai chalisa", "shirdi sai mantra", "shirdi sai kirtan",
    "sai ram sai ram", "sai ram sai ram song", "sai ram sai ram bhajan",
    "om sai ram", "om sai ram 108 times", "om sai ram mantra",
    "sai baba ki aarti", "sai baba ki aarti lyrics", "sai baba aarti song",
    "sai baba Thursday bhajan", "sai baba Thursday song", "sai baba Thursday aarti",
    "sai baba vrat katha", "sai baba vrat bhajan", "sai baba vrat song",
    "sai baba bhajan hindi", "sai baba bhajan marathi", "sai baba bhajan telugu",
    "sai baba bhajan kannada", "sai baba bhajan tamil", "sai baba bhajan gujarati",
    "sai baba bhajan bengali", "sai baba bhajan odia", "sai baba bhajan sindhi",
    
    # --- Other Devotional ---
    "vishnu bhajan", "vishnu song", "vishnu aarti", "vishnu chalisa",
    "vishnu mantra", "vishnu sahasranamam", "vishnu sahasranamam full",
    "vishnu sahasranamam by ms subbulakshmi", "vishnu kirtan",
    "narayan bhajan", "narayan song", "narayan aarti", "narayan kirtan",
    "venkateswara bhajan", "venkateswara song", "venkateswara aarti",
    "venkateswara suprabhatam", "venkateswara kirtan", "balaji bhajan",
    "balaji song", "balaji aarti", "balaji chalisa", "balaji kirtan",
    "tirupati balaji bhajan", "tirupati balaji song", "tirupati balaji aarti",
    "govinda bhajan", "govinda song", "govinda aarti", "govinda kirtan",
    "govinda govinda song", "govinda govinda bhajan",
    "murugan bhajan", "murugan song", "murugan aarti", "murugan kavadi",
    "murugan kirtan", "murugan mantra", "murugan chalisa",
    "ayyappa bhajan", "ayyappa song", "ayyappa aarti", "ayyappa kirtan",
    "ayyappa mantra", "sabarimala song", "sabarimala bhajan",
    "surya bhajan", "surya song", "surya aarti", "surya mantra",
    "surya namaskar mantra", "aditya hridayam", "aditya hridayam full",
    "chandra bhajan", "chandra song", "chandra aarti", "chandra mantra",
    "shani bhajan", "shani song", "shani aarti", "shani chalisa",
    "shani mantra", "shani kirtan", "shani dev bhajan", "shani dev song",
    "shani dev aarti", "shani dev chalisa", "shani dev mantra",
    "rahu ketu bhajan", "rahu ketu song", "rahu ketu mantra",
    "navagraha bhajan", "navagraha song", "navagraha mantra",
    "navagraha stotram", "navagraha kirtan",
    "santoshi mata bhajan", "santoshi mata song", "santoshi mata aarti",
    "santoshi mata chalisa", "santoshi mata kirtan", "santoshi mata mantra",
    "santoshi mata vrat katha", "santoshi mata vrat bhajan",
    "sheetla mata bhajan", "sheetla mata song", "sheetla mata aarti",
    "sheetla mata chalisa", "sheetla mata kirtan",
    "khodiyar mata bhajan", "khodiyar mata song", "khodiyar mata aarti",
    "bahuchara mata bhajan", "bahuchara mata song", "bahuchara mata aarti",
    "gatral mata bhajan", "gatral mata song", "gatral mata aarti",
    "vindhyavasini bhajan", "vindhyavasini song", "vindhyavasini aarti",
    "chintpurni bhajan", "chintpurni song", "chintpurni aarti",
    "jwalaji bhajan", "jwalaji song", "jwalaji aarti",
    "kamakhya bhajan", "kamakhya song", "kamakhya aarti",
    "tulja bhajan", "tulja song", "tulja aarti",
    "mahalaxmi bhajan", "mahalaxmi song", "mahalaxmi aarti",
    "kolhapur mahalaxmi bhajan", "kolhapur mahalaxmi song",
    
    # --- Sufi / Qawwali ---
    "sufi song", "sufi song hindi", "sufi kalam", "sufi poetry",
    "qawwali", "qawwali song", "qawwali new", "qawwali best",
    "qawwali by nusrat fateh ali khan", "nusrat fateh ali khan qawwali",
    "nusrat fateh ali khan song", "nusrat fateh ali khan best",
    "rahat fateh ali khan qawwali", "rahat fateh ali khan song",
    "sabri brothers qawwali", "sabri brothers song",
    "aziz mian qawwali", "aziz mian song",
    "badar miandad qawwali", "badar miandad song",
    "qawwali by rahat fateh ali khan", "qawwali by sabri brothers",
    "dama dam mast qalandar", "dama dam mast qalandar qawwali",
    "lal meri pat", "lal meri pat qawwali",
    "mere rashke qamar", "mere rashke qamar qawwali",
    "bhar do jholi meri", "bhar do jholi meri qawwali",
    "tajdar e haram", "tajdar e haram qawwali",
    "kun faya kun", "kun faya kun song", "kun faya kun arijit singh",
    "piya haji ali", "piya haji ali song", "piya haji ali qawwali",
    "khwaja mere khwaja", "khwaja mere khwaja song",
    "khwaja mere khwaja qawwali", "khwaja ji song",
    "ajmer sharif qawwali", "ajmer sharif song", "ajmer sharif bhajan",
    "khwaja garib nawaz song", "khwaja garib nawaz qawwali",
    "khwaja garib nawaz bhajan", "khwaja garib nawaz kirtan",
    "bulleh shah kalam", "bulleh shah song", "bulleh shah sufi",
    "bulleh shah poetry", "bulleh shah kafi",
    "baba bulleh shah", "baba bulleh shah kalam", "baba bulleh shah song",
    "shah hussain kalam", "shah hussain song", "shah hussain sufi",
    "baba farid kalam", "baba farid song", "baba farid sufi",
    "amir khusro kalam", "amir khusro song", "amir khusro sufi",
    "rumi poetry", "rumi song", "rumi sufi", "rumi kalam",
    "hafiz poetry", "hafiz song", "hafiz sufi",
    "sufi kirtan", "sufi bhajan", "sufi meditation", "sufi music",
    
    # --- Gurbani / Sikh ---
    "gurbani shabad", "gurbani shabad new", "gurbani shabad 2024",
    "gurbani shabad 2025", "gurbani kirtan", "gurbani song",
    "gurbani path", "gurbani waheguru", "gurbani simran",
    "waheguru simran", "waheguru jaap", "waheguru mantra",
    "waheguru simran 108 times", "waheguru jaap 108 times",
    "gurbani shabad by bhai harjinder singh", "bhai harjinder singh shabad",
    "bhai harjinder singh kirtan", "bhai harjinder singh song",
    "gurbani shabad by bhai manpreet singh", "bhai manpreet singh shabad",
    "bhai manpreet singh kirtan", "bhai manpreet singh song",
    "gurbani shabad by bhai gurpreet singh", "bhai gurpreet singh shabad",
    "bhai gurpreet singh kirtan", "bhai gurpreet singh song",
    "gurbani shabad by bhai jasbir singh", "bhai jasbir singh shabad",
    "bhai jasbir singh kirtan", "bhai jasbir singh song",
    "gurbani shabad by bhai ravinder singh", "bhai ravinder singh shabad",
    "bhai ravinder singh kirtan", "bhai ravinder singh song",
    "gurbani shabad by bhai satvinder singh", "bhai satvinder singh shabad",
    "gurbani shabad by bhai balwinder singh", "bhai balwinder singh shabad",
    "gurbani shabad by bhai lakhwinder singh", "bhai lakhwinder singh shabad",
    "japji sahib", "japji sahib full", "japji sahib path",
    "japji sahib by bhai harjinder singh", "japji sahib by bhai manpreet singh",
    "jaap sahib", "jaap sahib full", "jaap sahib path",
    "jaap sahib by bhai harjinder singh", "jaap sahib by bhai manpreet singh",
    "tav prasad savaiye", "tav prasad savaiye full", "tav prasad savaiye path",
    "chaupai sahib", "chaupai sahib full", "chaupai sahib path",
    "anand sahib", "anand sahib full", "anand sahib path",
    "rehras sahib", "rehras sahib full", "rehras sahib path",
    "kirtan sohila", "kirtan sohila full", "kirtan sohila path",
    "sukhmani sahib", "sukhmani sahib full", "sukhmani sahib path",
    "sukhmani sahib by bhai harjinder singh", "sukhmani sahib by bhai manpreet singh",
    "asa di var", "asa di var full", "asa di var path",
    "shabad hazare", "shabad hazare full", "shabad hazare path",
    "barah mah", "barah mah full", "barah mah path",
    "guru granth sahib", "guru granth sahib path", "guru granth sahib kirtan",
    "guru nanak dev ji", "guru nanak dev ji song", "guru nanak dev ji kirtan",
    "guru nanak dev ji shabad", "guru nanak dev ji bhajan",
    "guru gobind singh ji", "guru gobind singh ji song",
    "guru gobind singh ji kirtan", "guru gobind singh ji shabad",
    "guru ram das ji", "guru ram das ji song", "guru ram das ji kirtan",
    "guru arjan dev ji", "guru arjan dev ji song", "guru arjan dev ji kirtan",
    "guru hargobind ji", "guru hargobind ji song", "guru hargobind ji kirtan",
    "guru har rai ji", "guru har rai ji song", "guru har rai ji kirtan",
    "guru har krishan ji", "guru har krishan ji song", "guru har krishan ji kirtan",
    "guru tegh bahadur ji", "guru tegh bahadur ji song", "guru tegh bahadur ji kirtan",
    "guru granth sahib ji", "guru granth sahib ji song", "guru granth sahib ji kirtan",
    
    # --- Buddhist / Jain ---
    "buddhist song", "buddhist chant", "buddhist mantra",
    "buddha mantra", "buddha song", "buddha bhajan",
    "buddha vandana", "buddha kirtan", "buddha meditation",
    "om mani padme hum", "om mani padme hum 108 times",
    "buddham saranam gacchami", "buddham saranam gacchami chant",
    "jain song", "jain bhajan", "jain stuti", "jain mantra",
    "mahavir bhajan", "mahavir song", "mahavir mantra",
    "mahavir stuti", "mahavir kirtan", "mahavir vandana",
    "navkar mantra", "navkar mantra 108 times", "navkar mantra jaap",
    "namokar mantra", "namokar mantra 108 times", "namokar mantra jaap",
    "bhaktamar stotra", "bhaktamar stotra full", "bhaktamar stotra path",
    "ujjayini mahakal bhajan", "mahakal song", "mahakal bhajan",
    "mahakal aarti", "mahakal mantra", "mahakal kirtan",
    "mahakaleshwar bhajan", "mahakaleshwar song", "mahakaleshwar aarti",
    "mahakaleshwar mantra", "mahakaleshwar kirtan",
    "somnath bhajan", "somnath song", "somnath aarti",
    "somnath mantra", "somnath kirtan",
    "kedarnath bhajan", "kedarnath song", "kedarnath aarti",
    "kedarnath mantra", "kedarnath kirtan",
    "badrinath bhajan", "badrinath song", "badrinath aarti",
    "badrinath mantra", "badrinath kirtan",
    "jagannath bhajan", "jagannath song", "jagannath aarti",
    "jagannath mantra", "jagannath kirtan", "jagannath rath yatra song",
    "puri jagannath bhajan", "puri jagannath song", "puri jagannath aarti",
    "tirupati balaji bhajan", "tirupati balaji song", "tirupati balaji aarti",
    "tirupati balaji suprabhatam", "tirupati balaji kirtan",
    "venkateswara suprabhatam", "venkateswara suprabhatam full",
    "govinda govinda", "govinda govinda song", "govinda govinda bhajan",
    "govinda govinda kirtan", "govinda govinda aarti",
    "srinivasa bhajan", "srinivasa song", "srinivasa aarti",
    "srinivasa kirtan", "srinivasa mantra",
    
    # --- More Devotional / Regional ---
    "tulsi bhajan", "tulsi song", "tulsi aarti", "tulsi mantra",
    "tulsi vivah song", "tulsi vivah bhajan", "tulsi vivah katha",
    "tulsi das bhajan", "tulsi das song", "tulsi das kirtan",
    "meera bhajan", "meera song", "meera kirtan", "meera bhajan hindi",
    "meera bhajan by anuradha paudwal", "meera bhajan by lata mangeshkar",
    "meera bhajan by ms subbulakshmi", "meera bhajan by m s subbulakshmi",
    "surdas bhajan", "surdas song", "surdas kirtan", "surdas bhajan hindi",
    "kabir bhajan", "kabir song", "kabir kirtan", "kabir bhajan hindi",
    "kabir doha", "kabir doha song", "kabir vani", "kabir vani song",
    "ravidas bhajan", "ravidas song", "ravidas kirtan", "ravidas bhajan hindi",
    "ravidas vani", "ravidas vani song", "ravidas kirtan",
    "namdev bhajan", "namdev song", "namdev kirtan", "namdev bhajan hindi",
    "namdev vani", "namdev vani song", "namdev kirtan",
    "daddu bhajan", "daddu song", "daddu kirtan",
    "pipa bhajan", "pipa song", "pipa kirtan",
    "sadna bhajan", "sadna song", "sadna kirtan",
    "dhanna bhajan", "dhanna song", "dhanna kirtan",
    "trilochan bhajan", "trilochan song", "trilochan kirtan",
    "beni bhajan", "beni song", "beni kirtan",
    "guru nanak bhajan", "guru nanak song", "guru nanak kirtan",
    "guru nanak vani", "guru nanak vani song", "guru nanak kirtan",
    "guru angad bhajan", "guru angad song", "guru angad kirtan",
    "guru amar das bhajan", "guru amar das song", "guru amar das kirtan",
    "guru ram das bhajan", "guru ram das song", "guru ram das kirtan",
    "guru arjan bhajan", "guru arjan song", "guru arjan kirtan",
    "guru hargobind bhajan", "guru hargobind song", "guru hargobind kirtan",
    "guru har rai bhajan", "guru har rai song", "guru har rai kirtan",
    "guru har krishan bhajan", "guru har krishan song", "guru har krishan kirtan",
    "guru tegh bahadur bhajan", "guru tegh bahadur song", "guru tegh bahadur kirtan",
    "guru gobind singh bhajan", "guru gobind singh song", "guru gobind singh kirtan",
    "guru granth sahib bhajan", "guru granth sahib song", "guru granth sahib kirtan",
    
    # ---------- Indie / Pop / Misc ----------
    "indian pop song", "indie hindi song", "hindi indie music",
    "bollywood mashup", "hindi remix song", "hindi dj song",
    "90s bollywood song", "2000s hindi song", "2010s hindi song",
    "hindi cover song", "hindi unplugged song", "acoustic hindi song",
    "hindi rap song", "indian rap song", "desi hip hop",
    "hindi instrumental", "sitar instrumental", "flute instrumental",
    "tabla instrumental", "santoor instrumental",
    "hindi classical instrumental", "hindi fusion music",
    "hindustani classical vocal", "hindustani classical instrumental",
    "carnatic vocal", "carnatic instrumental",
    "indian jazz", "indian fusion", "indian electronic music",
    "indian edm", "indian house music", "indian techno",
    "indian indie pop", "indian indie rock", "indian alternative",
    "hindi rock song", "hindi metal song", "hindi punk song",
    "hindi emo song", "hindi sad rap", "hindi love rap",
    "hindi romantic rap", "hindi party rap", "hindi gangster rap",
    "desi hip hop new", "desi hip hop 2024", "desi hip hop 2025",
    "indian drill", "desi drill", "hindi drill",
    "indian trap", "desi trap", "hindi trap",
    "indian lo-fi", "desi lo-fi", "hindi lo-fi",
    "indian chillhop", "desi chillhop", "hindi chillhop",
    "indian study music", "desi study music", "hindi study music",
    "indian focus music", "desi focus music", "hindi focus music",
    "indian meditation music", "desi meditation music", "hindi meditation music",
    "indian yoga music", "desi yoga music", "hindi yoga music",
    "indian spa music", "desi spa music", "hindi spa music",
    "indian sleep music", "desi sleep music", "hindi sleep music",
    "indian relaxing music", "desi relaxing music", "hindi relaxing music",
    "indian calming music", "desi calming music", "hindi calming music",
    
    # ---------- International (popular in India) ----------
    "english pop song", "english romantic song", "english sad song",
    "english party song", "english old song", "english new song 2025",
    "ed sheeran song", "justin bieber song", "taylor swift song",
    "weeknd song", "drake song", "billie eilish song",
    "korean song", "kpop song", "bts song", "blackpink song",
    "spanish song", "arabic song", "turkish song",
    "english love song", "english breakup song", "english heartbreak song",
    "english dance song", "english edm", "english remix",
    "english lofi", "english chill song", "english study song",
    "english sleep song", "english relaxing song", "english meditation song",
    "ed sheeran romantic song", "ed sheeran sad song", "ed sheeran new song",
    "justin bieber romantic song", "justin bieber sad song", "justin bieber new song",
    "taylor swift romantic song", "taylor swift sad song", "taylor swift new song",
    "weeknd romantic song", "weeknd sad song", "weeknd new song",
    "drake song", "drake rap", "drake new song", "drake hit song",
    "billie eilish sad song", "billie eilish new song", "billie eilish hit song",
    "bts song", "bts new song", "bts hit song", "bts romantic song",
    "blackpink song", "blackpink new song", "blackpink hit song",
    "kpop new song", "kpop hit song", "kpop romantic song",
    "korean romantic song", "korean sad song", "korean drama song",
    "korean ost", "korean drama ost", "korean pop song",
    "spanish song", "spanish romantic song", "spanish party song",
    "spanish new song", "spanish hit song", "spanish latin song",
    "arabic song", "arabic romantic song", "arabic sad song",
    "arabic new song", "arabic hit song", "arabic pop song",
    "turkish song", "turkish romantic song", "turkish sad song",
    "turkish new song", "turkish hit song", "turkish pop song",
    "english cover song", "english mashup", "english remix song",
    "english acoustic song", "english unplugged song", "english live song",
    "english instrumental", "english piano instrumental", "english guitar instrumental",
    "english violin instrumental", "english saxophone instrumental",
    "english jazz", "english blues", "english rock song",
    "english metal song", "english punk song", "english indie song",
    "english alternative song", "english electronic song", "english house song",
    "english techno song", "english trap song", "english drill song",
    "english hip hop", "english rap song", "english r&b song",
    "english soul song", "english funk song", "english disco song",
    "english country song", "english folk song", "english classical song",
    
    # ---------- More Hindi evergreen / hits ----------
    "hindi 90s hit song", "hindi 80s hit song", "hindi 70s hit song",
    "kumar sanu hit song", "udit narayan hit song", "alka yagnik hit song",
    "asha bhosle hit song", "lata mangeshkar hit song",
    "mohammed rafi hit song", "kishore kumar hit song",
    "hindi sad love song", "hindi romantic hits 2024",
    "hindi romantic hits 2025", "bollywood top 10 song",
    "bollywood top 20 song", "bollywood chartbuster",
    "hindi trending song", "hindi viral song", "hindi reels song",
    "instagram trending hindi song", "youtube trending hindi song",
    "hindi 90s romantic song", "hindi 90s sad song", "hindi 90s party song",
    "hindi 80s romantic song", "hindi 80s sad song", "hindi 80s party song",
    "hindi 70s romantic song", "hindi 70s sad song", "hindi 70s party song",
    "hindi 60s romantic song", "hindi 60s sad song", "hindi 60s party song",
    "hindi old is gold", "hindi old romantic song", "hindi old sad song",
    "hindi old party song", "hindi old dance song", "hindi old melody song",
    "hindi retro song", "hindi vintage song", "hindi classic song",
    "hindi timeless song", "hindi evergreen romantic song",
    "hindi evergreen sad song", "hindi evergreen party song",
    "hindi superhit song", "hindi blockbuster song", "hindi hit list",
    "hindi top 50 song", "hindi top 100 song", "hindi best song",
    "hindi best romantic song", "hindi best sad song", "hindi best party song",
    "hindi best dance song", "hindi best love song", "hindi best breakup song",
    "hindi best friendship song", "hindi best motivational song",
    "hindi best devotional song", "hindi best bhajan", "hindi best kirtan",
    "hindi best sufi song", "hindi best qawwali", "hindi best ghazal",
    "hindi best classical song", "hindi best instrumental",
    "hindi best lofi", "hindi best remix", "hindi best dj song",
    "hindi best mashup", "hindi best cover", "hindi best unplugged",
    "hindi best acoustic", "hindi best rap", "hindi best hip hop",
    "hindi best indie", "hindi best pop", "hindi best rock",
    "hindi best metal", "hindi best punk", "hindi best emo",
    "hindi best electronic", "hindi best edm", "hindi best house",
    "hindi best techno", "hindi best trap", "hindi best drill",
    
    # ---------- More Bhajan / Devotional (additional) ----------
    "mata ke bhajan", "mata ke bhajan new", "mata ke bhajan 2024",
    "mata ke bhajan 2025", "mata ke bhajan hindi", "mata ke bhajan best",
    "mata ke bhajan by anuradha paudwal", "mata ke bhajan by narendra chanchal",
    "mata ke bhajan by gulshan kumar", "mata ke bhajan by hari om sharan",
    "devi bhajan", "devi bhajan new", "devi bhajan 2024", "devi bhajan 2025",
    "devi bhajan hindi", "devi bhajan best", "devi bhajan by anuradha paudwal",
    "devi bhajan by narendra chanchal", "devi bhajan by gulshan kumar",
    "devi bhajan by hari om sharan", "devi kirtan", "devi aarti",
    "devi chalisa", "devi mantra", "devi stuti", "devi vandana",
    "shakti bhajan", "shakti song", "shakti aarti", "shakti mantra",
    "shakti kirtan", "shakti chalisa", "shakti stuti", "shakti vandana",
    "shakti peeth bhajan", "shakti peeth song", "shakti peeth aarti",
    "shakti peeth kirtan", "shakti peeth mantra", "shakti peeth chalisa",
    "nav durga bhajan", "nav durga song", "nav durga aarti",
    "nav durga kirtan", "nav durga mantra", "nav durga chalisa",
    "nav durga stuti", "nav durga vandana", "nav durga kavach",
    "durga kavach", "durga kavach full", "durga kavach path",
    "durga kavach by gulshan kumar", "durga kavach by anuradha paudwal",
    "argala stotram", "argala stotram full", "argala stotram path",
    "keelak stotram", "keelak stotram full", "keelak stotram path",
    "kavach stotram", "kavach stotram full", "kavach stotram path",
    "ratri sukta", "ratri sukta full", "ratri sukta path",
    "devi sukta", "devi sukta full", "devi sukta path",
    "durga sukta", "durga sukta full", "durga sukta path",
    "sri sukta", "sri sukta full", "sri sukta path",
    "bhuvaneshwari bhajan", "bhuvaneshwari song", "bhuvaneshwari aarti",
    "bhuvaneshwari mantra", "bhuvaneshwari kirtan", "bhuvaneshwari chalisa",
    "bhuvaneshwari stuti", "bhuvaneshwari vandana", "bhuvaneshwari kavach",
    "baglamukhi bhajan", "baglamukhi song", "baglamukhi aarti",
    "baglamukhi mantra", "baglamukhi kirtan", "baglamukhi chalisa",
    "baglamukhi stuti", "baglamukhi vandana", "baglamukhi kavach",
    "matangi bhajan", "matangi song", "matangi aarti",
    "matangi mantra", "matangi kirtan", "matangi chalisa",
    "kamla bhajan", "kamla song", "kamla aarti",
    "kamla mantra", "kamla kirtan", "kamla chalisa",
    "tara bhajan", "tara song", "tara aarti",
    "tara mantra", "tara kirtan", "tara chalisa",
    "chhinnamasta bhajan", "chhinnamasta song", "chhinnamasta aarti",
    "chhinnamasta mantra", "chhinnamasta kirtan", "chhinnamasta chalisa",
    "dhumavati bhajan", "dhumavati song", "dhumavati aarti",
    "dhumavati mantra", "dhumavati kirtan", "dhumavati chalisa",
    "bhairavi bhajan", "bhairavi song", "bhairavi aarti",
    "bhairavi mantra", "bhairavi kirtan", "bhairavi chalisa",
    "dash mahavidya bhajan", "dash mahavidya song", "dash mahavidya aarti",
    "dash mahavidya mantra", "dash mahavidya kirtan", "dash mahavidya chalisa",
    
    # ---------- More specific / long-tail (additional) ----------
    "hindi song 2024 new", "hindi song 2024 hit", "hindi song 2024 romantic",
    "hindi song 2024 sad", "hindi song 2024 party", "hindi song 2024 dance",
    "hindi song 2025 new", "hindi song 2025 hit", "hindi song 2025 romantic",
    "hindi song 2025 sad", "hindi song 2025 party", "hindi song 2025 dance",
    "hindi song 2026 new", "hindi song 2026 hit", "hindi song 2026 romantic",
    "hindi song 2026 sad", "hindi song 2026 party", "hindi song 2026 dance",
    "bollywood song 2024 new", "bollywood song 2024 hit", "bollywood song 2024 romantic",
    "bollywood song 2024 sad", "bollywood song 2024 party", "bollywood song 2024 dance",
    "bollywood song 2025 new", "bollywood song 2025 hit", "bollywood song 2025 romantic",
    "bollywood song 2025 sad", "bollywood song 2025 party", "bollywood song 2025 dance",
    "bollywood song 2026 new", "bollywood song 2026 hit", "bollywood song 2026 romantic",
    "bollywood song 2026 sad", "bollywood song 2026 party", "bollywood song 2026 dance",
    "punjabi song 2024 new", "punjabi song 2024 hit", "punjabi song 2024 romantic",
    "punjabi song 2024 sad", "punjabi song 2024 party", "punjabi song 2024 dance",
    "punjabi song 2025 new", "punjabi song 2025 hit", "punjabi song 2025 romantic",
    "punjabi song 2025 sad", "punjabi song 2025 party", "punjabi song 2025 dance",
    "punjabi song 2026 new", "punjabi song 2026 hit", "punjabi song 2026 romantic",
    "punjabi song 2026 sad", "punjabi song 2026 party", "punjabi song 2026 dance",
    "bhojpuri song 2024 new", "bhojpuri song 2024 hit", "bhojpuri song 2024 romantic",
    "bhojpuri song 2024 sad", "bhojpuri song 2024 party", "bhojpuri song 2024 dance",
    "bhojpuri song 2025 new", "bhojpuri song 2025 hit", "bhojpuri song 2025 romantic",
    "bhojpuri song 2025 sad", "bhojpuri song 2025 party", "bhojpuri song 2025 dance",
    "bhojpuri song 2026 new", "bhojpuri song 2026 hit", "bhojpuri song 2026 romantic",
    "bhojpuri song 2026 sad", "bhojpuri song 2026 party", "bhojpuri song 2026 dance",
    
    # ---------- Trending / Viral (additional) ----------
    "trending hindi song", "trending bollywood song", "trending punjabi song",
    "trending bhojpuri song", "trending devotional song", "trending bhajan",
    "trending kirtan", "trending sufi song", "trending qawwali",
    "trending ghazal", "trending classical song", "trending instrumental",
    "trending lofi", "trending remix", "trending dj song",
    "trending mashup", "trending cover", "trending unplugged",
    "trending acoustic", "trending rap", "trending hip hop",
    "trending indie", "trending pop", "trending rock",
    "trending metal", "trending punk", "trending emo",
    "trending electronic", "trending edm", "trending house",
    "trending techno", "trending trap", "trending drill",
    "viral hindi song", "viral bollywood song", "viral punjabi song",
    "viral bhojpuri song", "viral devotional song", "viral bhajan",
    "viral kirtan", "viral sufi song", "viral qawwali",
    "viral ghazal", "viral classical song", "viral instrumental",
    "viral lofi", "viral remix", "viral dj song",
    "viral mashup", "viral cover", "viral unplugged",
    "viral acoustic", "viral rap", "viral hip hop",
    "viral indie", "viral pop", "viral rock",
    "viral metal", "viral punk", "viral emo",
    "viral electronic", "viral edm", "viral house",
    "viral techno", "viral trap", "viral drill",
]

YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': 'in_playlist',
    'skip_download': True,
    'default_search': 'ytsearch30',
}

AUTO_JOBS = {}

# --- GLOBAL JOB QUEUE ---
JOB_QUEUE: asyncio.Queue = None
WORKER_TASK = None
SENT_IDS_LOCK = None


def _init_globals():
    global JOB_QUEUE, SENT_IDS_LOCK
    if JOB_QUEUE is None:
        JOB_QUEUE = asyncio.Queue()
    if SENT_IDS_LOCK is None:
        SENT_IDS_LOCK = asyncio.Lock()


# ---------- DATABASE ----------
def load_sent_ids():
    if not os.path.exists(DB_FILE):
        return set()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f).get("sent_ids", []))
    except Exception as e:
        print(f"DB load error: {e}")
        return set()


def save_sent_ids(sent_ids: set):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"sent_ids": list(sent_ids)}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"DB save error: {e}")


# ---------- SEARCH ----------
def search_random_song(query: str, sent_ids: set):
    try:
        opts = dict(YDL_OPTS)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch30:{query}", download=False)
    except Exception as e:
        return None, f"YouTube search fail (yt-dlp): {e}"

    entries = info.get('entries', []) or []
    if not entries:
        return None, f"'{query}' ke liye YouTube pe koi result nahi mila"

    total = len(entries)
    skipped_sent = 0
    skipped_long = 0
    skipped_bad = 0
    fresh = []

    for v in entries:
        vid = v.get('id')
        dur = v.get('duration')
        title = (v.get('title') or '').lower()

        if not vid:
            continue
        if vid in sent_ids:
            skipped_sent += 1
            continue

        if dur is not None:
            if dur > MAX_DURATION or dur < MIN_DURATION:
                skipped_long += 1
                continue

        bad_words = [
            "slowed", "reverb", "lofi edit", "8d audio",
            "nightcore", "slowed+reverb", "slowed -reverb",
            "slowed-reverb",
        ]
        if any(w in title for w in bad_words):
            skipped_bad += 1
            continue

        fresh.append(v)

    if not fresh:
        reason = (
            f"'{query}': {total} results mein se sab filter:\n"
            f"  • Already bheje: {skipped_sent}\n"
            f"  • Bahut lambe/chhote: {skipped_long}\n"
            f"  • Lofi/slowed: {skipped_bad}"
        )
        return None, reason

    video = random.choice(fresh)
    return {
        'id': video.get('id'),
        'title': video.get('title') or 'Unknown',
        'url': f"https://youtu.be/{video.get('id')}",
    }, None


# ---------- API DOWNLOAD ----------
def download_from_api(video_url: str, media_type: str = "audio"):
    """
    media_type: "audio" or "video"
    Return: (details_dict, file_path_or_None)
    """
    params = {"url": video_url, "type": media_type, "api_key": API_KEY}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }

    details = {"status_code": None, "content_type": None,
               "content_length": None, "file_path": None,
               "error": None, "error_type": None, "attempts": 0,
               "media_type": media_type}

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        details["attempts"] = attempt
        try:
            r = requests.get(API_URL, params=params, headers=headers,
                             stream=True, timeout=300)
            details["status_code"] = r.status_code
            details["content_type"] = r.headers.get("Content-Type")
            details["content_length"] = r.headers.get("Content-Length")

            ctype = (details["content_type"] or "").lower()

            if r.status_code == 200 and media_type == "audio" and "audio" in ctype:
                ext = "m4a" if ("m4a" in ctype or "mp4" in ctype) else \
                      "mp3" if "mpeg" in ctype else "m4a"
                file_path = f"temp_audio_{random.randint(100000, 999999)}.{ext}"
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                details["file_path"] = file_path
                details["error"] = None
                details["error_type"] = None
                return details, file_path

            if r.status_code == 200 and media_type == "video" and "video" in ctype:
                ext = "mp4" if "mp4" in ctype else "mkv" if "matroska" in ctype else "mp4"
                file_path = f"temp_video_{random.randint(100000, 999999)}.{ext}"
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                details["file_path"] = file_path
                details["error"] = None
                details["error_type"] = None
                return details, file_path

            details["error_type"] = "API"
            try:
                err_json = r.json()
                details["error"] = (
                    f"API ne HTTP {r.status_code} diya (expected {media_type})\n"
                    f"Content-Type: {details['content_type']}\n"
                    f"Response: {err_json}"
                )
            except Exception:
                text = r.text[:300] if r.text else "(empty body)"
                details["error"] = (
                    f"API ne HTTP {r.status_code} diya (expected {media_type})\n"
                    f"Content-Type: {details['content_type']}\n"
                    f"Response: {text}"
                )

            print(f"⚠️ API attempt {attempt}/{max_retries}: {details['error']}")

        except requests.exceptions.Timeout:
            details["error_type"] = "API"
            details["error"] = "API request timeout (300s) — server slow hai"
            print(f"⚠️ Timeout attempt {attempt}/{max_retries}")

        except requests.exceptions.ConnectionError as e:
            details["error_type"] = "API"
            details["error"] = f"API se connect nahi ho paya: {e}"
            print(f"⚠️ Connection error attempt {attempt}/{max_retries}")

        except Exception as e:
            details["error_type"] = "API"
            details["error"] = f"API request exception: {e}"
            print(f"⚠️ Exception attempt {attempt}/{max_retries}: {e}")

        if attempt < max_retries:
            time.sleep(2 ** attempt)

    return details, None


# ---------- SEND ONE FORMAT ----------
async def _send_one_format(chat, result: dict, media_type: str, prefix: str):
    """
    Ek specific format (audio OR video) download karke bhejo.
    Return: (success: bool, message: str)
    """
    loop = asyncio.get_running_loop()

    try:
        details, file_path = await loop.run_in_executor(
            None, download_from_api, result['url'], media_type
        )
    except Exception as e:
        return False, (
            "🟡 BOT ERROR\n"
            "─────────────────\n"
            f"{media_type} download exception: {e}"
        )

    if not file_path or not os.path.exists(file_path):
        return False, (
            f"🔴 API ERROR ({media_type.upper()})\n"
            "─────────────────\n"
            f"🎵 {result['title']}\n"
            f"🔗 {result['url']}\n\n"
            f"Status: {details.get('status_code')}\n"
            f"Type: {details.get('content_type')}\n"
            f"Attempts: {details.get('attempts')}\n\n"
            f"Error: {details.get('error') or 'Unknown'}"
        )

    try:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        limit = 50
        if size_mb > limit:
            msg = (
                "🟡 BOT ERROR\n"
                "─────────────────\n"
                f"{media_type.capitalize()} {size_mb:.1f} MB — Telegram limit ({limit}MB).\n"
                f"🔗 {result['url']}"
            )
            os.remove(file_path)
            return False, msg

        with open(file_path, "rb") as media:
            if media_type == "audio":
                await chat.send_audio(
                    audio=media,
                    title=result['title'][:60],
                    caption=f"{prefix}🎵 {result['title']}\n🔗 {result['url']}",
                    read_timeout=300, write_timeout=300, connect_timeout=60,
                )
            else:
                await chat.send_video(
                    video=media,
                    caption=f"{prefix}🎬 {result['title']}\n🔗 {result['url']}",
                    supports_streaming=True,
                    read_timeout=300, write_timeout=300, connect_timeout=60,
                )
        print(f"✅ Sent {media_type}: {result['title']}")
        return True, "OK"

    except Exception as e:
        return False, (
            "🟡 BOT ERROR (Telegram send)\n"
            "─────────────────\n"
            f"{media_type} send error: {e}\n"
            f"🔗 {result['url']}"
        )

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


# ---------- CORE: SEND BOTH AUDIO + VIDEO ----------
async def send_both_formats(chat, sent_ids: set, prefix: str = ""):
    """
    Ek song search karo → pehle audio, phir video bhejo (dono same song ka).
    Return: (success: bool, message: str)
    """
    # -------- SEARCH --------
    result = None
    search_errors = []
    queries = random.sample(SEARCH_QUERIES, len(SEARCH_QUERIES))
    loop = asyncio.get_running_loop()

    for q in queries:
        try:
            res, err = await loop.run_in_executor(
                None, search_random_song, q, sent_ids
            )
        except Exception as e:
            res, err = None, f"search exception: {e}"

        if res:
            result = res
            break
        if err:
            search_errors.append(err)

    if not result:
        err_text = "\n\n".join(search_errors[-2:]) if search_errors else "Unknown search issue"
        return False, (
            "🟢 SEARCH ERROR\n"
            "─────────────────\n"
            "Koi bhi naya song nahi mila.\n\n"
            f"{err_text}\n\n"
            "👉 /reset try karein."
        )

    # mark as sent
    async with SENT_IDS_LOCK:
        sent_ids.add(result['id'])
        save_sent_ids(sent_ids)

    print(f"🎯 Selected: {result['title']}")

    # -------- SEND AUDIO FIRST --------
    ok_a, msg_a = await _send_one_format(chat, result, "audio", prefix=prefix)
    if not ok_a:
        try:
            await chat.send_message("⚠️ Audio fail:\n\n" + msg_a)
        except Exception:
            pass

    # -------- THEN SEND VIDEO --------
    ok_v, msg_v = await _send_one_format(chat, result, "video", prefix=prefix)
    if not ok_v:
        try:
            await chat.send_message("⚠️ Video fail:\n\n" + msg_v)
        except Exception:
            pass

    if ok_a or ok_v:
        return True, "OK"
    return False, "Dono format fail ho gaye."


# ---------- WORKER (batching) ----------
async def worker_loop():
    print("🧵 Worker started.")
    while True:
        try:
            first_job = await JOB_QUEUE.get()
            print(f"📥 Job mila. Queue size: {JOB_QUEUE.qsize()}")

            batch_size = random.randint(BATCH_MIN, BATCH_MAX)
            batch = [first_job]
            for _ in range(batch_size - 1):
                try:
                    batch.append(JOB_QUEUE.get_nowait())
                except asyncio.QueueEmpty:
                    break

            print(f"📦 Processing batch of {len(batch)} job(s)")

            async def handle_job(job):
                chat = job["chat"]
                prefix = job.get("prefix", "")
                sent_ids = load_sent_ids()
                try:
                    ok, msg = await send_both_formats(chat, sent_ids, prefix=prefix)
                    if not ok:
                        try:
                            await chat.send_message(msg)
                        except Exception as e:
                            print(f"Error msg bhejne mein fail: {e}")
                except Exception as e:
                    print(f"handle_job error: {e}")
                    traceback.print_exc()

            await asyncio.gather(*(handle_job(j) for j in batch))
            await asyncio.sleep(random.uniform(BATCH_DELAY_MIN, BATCH_DELAY_MAX))

        except Exception as e:
            print(f"Worker loop error: {e}")
            traceback.print_exc()
            await asyncio.sleep(1)


def _ensure_worker_started():
    global WORKER_TASK
    _init_globals()
    if WORKER_TASK is None or WORKER_TASK.done():
        WORKER_TASK = asyncio.get_running_loop().create_task(worker_loop())
        print("🧵 Worker task created.")


# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _init_globals()
    await update.message.reply_text(
        "🙏 Welcome!\n\n"
        "Main ek music bot hoon 🎵🎬\n\n"
        "Commands:\n"
        "• /start - Welcome\n"
        "• /yt - Ek song ka AUDIO + VIDEO dono\n"
        "• /audio - Sirf audio\n"
        "• /video - Sirf video\n"
        "• /auto - Har 10 sec auto (audio+video)\n"
        "• /stop - Auto band\n"
        "• /reset - History clear"
    )


async def yt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ab /yt pe AUDIO + VIDEO dono aayenge."""
    _init_globals()
    _ensure_worker_started()
    await update.message.reply_text("🔎 Song dhoondh raha hoon — audio + video dono aayenge...")
    await JOB_QUEUE.put({
        "chat": update.effective_chat,
        "prefix": "",
    })


async def auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _init_globals()
    _ensure_worker_started()
    chat_id = update.effective_chat.id
    if chat_id in AUTO_JOBS:
        await update.message.reply_text("⚠️ Auto already chal raha hai. /stop se rok.")
        return

    context.chat_data["chat"] = update.effective_chat

    async def auto_job(ctx: ContextTypes.DEFAULT_TYPE):
        chat = ctx.chat_data.get("chat")
        if chat is None:
            return
        await JOB_QUEUE.put({
            "chat": chat,
            "prefix": "[AUTO] ",
        })

    job = context.job_queue.run_repeating(
        auto_job,
        interval=AUTO_INTERVAL,
        first=1,
        name=f"auto_{chat_id}",
        chat_id=chat_id,
    )
    AUTO_JOBS[chat_id] = job
    await update.message.reply_text(
        f"🚀 Auto ON! Har {AUTO_INTERVAL} sec ek song (audio + video) aayega.\n/stop se rok."
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    job = AUTO_JOBS.pop(chat_id, None)
    if job:
        job.schedule_removal()
        await update.message.reply_text("🛑 Auto OFF.")
    else:
        await update.message.reply_text("ℹ️ Auto chal nahi raha tha.")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _init_globals()
    async with SENT_IDS_LOCK:
        save_sent_ids(set())
    await update.message.reply_text("✅ History clear ho gayi.")


# ---------- POST INIT ----------
async def post_init(app):
    _ensure_worker_started()


# ---------- MAIN ----------
def main():
    request = HTTPXRequest(connect_timeout=60.0, read_timeout=300.0, write_timeout=300.0)
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .request(request)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yt", yt_command))
    app.add_handler(CommandHandler("auto", auto_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("reset", reset_command))

    print("Bot chal raha hai... (Ctrl+C to stop)")
    app.run_polling()


if __name__ == '__main__':
    main()