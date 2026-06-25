"""
Module 3 — Image Fetching
Pexels API → download images per chapter keyword (per-channel keywords)
"""

import os, requests, time

PEXELS_API = "https://api.pexels.com/v1/search"

# Per-channel keyword sets (9 chapters × 3 keywords each)
KEYWORDS_BY_CHANNEL = {
    "bodytruth": {
        0: ["spine xray anatomy", "human skeleton", "anatomy medical"],
        1: ["vertebrae spinal cord", "spine structure", "back anatomy"],
        2: ["brain neurons", "nervous system", "nerve signals"],
        3: ["mri scan medical", "disc herniation", "spinal disc"],
        4: ["sitting desk posture", "back pain office", "sedentary lifestyle"],
        5: ["chronic pain", "doctor hospital", "back surgery"],
        6: ["phone neck pain", "screen time posture", "office ergonomics"],
        7: ["yoga movement", "exercise fitness", "healthy posture"],
        8: ["nature peaceful", "body wellness", "health lifestyle"],
    },
    "wealthcodes": {
        0: ["money wealth abundance", "financial freedom success", "rich lifestyle luxury"],
        1: ["bible church faith", "prayer spiritual", "god blessing"],
        2: ["family estate mansion", "generational wealth family", "wealthy family home"],
        3: ["stock market chart", "compound interest investing", "financial growth profit"],
        4: ["bitcoin cryptocurrency", "digital finance blockchain", "crypto investment"],
        5: ["trust estate planning", "wealth protection insurance", "family legacy"],
        6: ["purpose driven mindset", "abundance mindset success", "motivation wealth"],
        7: ["financial plan budget", "savings investment goal", "money management"],
        8: ["financial independence", "passive income laptop", "investment portfolio"],
    },
    "cryptotruth": {
        0: ["bitcoin cryptocurrency", "blockchain technology", "digital currency"],
        1: ["crypto market chart", "trading screen", "financial technology"],
        2: ["ethereum defi", "digital wallet", "crypto coins"],
        3: ["bitcoin mining hardware", "server data center", "technology infrastructure"],
        4: ["crypto exchange trading", "market volatility", "investment risk"],
        5: ["decentralized finance", "smart contract", "blockchain network"],
        6: ["crypto wealth millionaire", "financial freedom digital", "bitcoin success"],
        7: ["regulation government finance", "policy financial", "compliance business"],
        8: ["future technology", "innovation digital", "financial revolution"],
    },
    "soccertruth": {
        # Hook — estádio lotado, troféu, clima épico da Copa
        0: ["world cup soccer stadium crowd", "football trophy gold", "soccer fans cheering stadium"],
        # GOAT debate — Messi, jogadas, Argentina, bola no pé
        1: ["soccer player dribbling ball", "football star goal celebration", "argentina soccer team"],
        # Pelé era — Brasil, futebol clássico, lenda histórica
        2: ["brazil football soccer", "soccer legend vintage", "football classic match crowd"],
        # Copa do Mundo — finais, comemorações, gols épicos
        3: ["soccer world cup final", "football championship celebration", "soccer goal kick"],
        # Gols e recordes — jogadas espetaculares, placar, estadio noturno
        4: ["soccer goal celebration crowd", "football match action night", "soccer spectacular play"],
        # Pelé no Cosmos / USA — futebol americano, New York, estádio EUA
        5: ["soccer USA america", "football new york stadium", "american soccer match"],
        # Estatísticas / debate GOAT — dados, análise, troféus
        6: ["football trophy collection", "soccer records statistics screen", "football champion award"],
        # Torcida / emoção — fãs apaixonados, bandeiras, festa nas arquibancadas
        7: ["soccer fans stadium flags", "football supporter passion", "soccer crowd celebration"],
        # Conclusão / próxima geração — crianças, futuro, sonho futebol
        8: ["soccer youth kid football", "children playing soccer field", "young football player"],
    },
    "catfacts": {
        0: ["cute cat kitten", "cat domestic pet", "kitten playing"],
        1: ["cat breed exotic", "persian cat", "siamese cat"],
        2: ["cat behavior sleeping", "cat stretching", "cat grooming"],
        3: ["cat hunting instinct", "cat jumping", "cat playing"],
        4: ["cat health veterinary", "cat care grooming", "pet health"],
        5: ["cat eyes close up", "cat senses", "cat curiosity"],
        6: ["cat communication meow", "cat body language", "cat expression"],
        7: ["cat wild lion", "big cat nature", "tiger wild animal"],
        8: ["cat human bond", "person cat together", "cat owner love"],
    },
    "luxurydogs": {
        0: ["luxury dog expensive breed", "rare dog purebred", "premium dog"],
        1: ["golden retriever dog", "labrador luxury", "dog breed beautiful"],
        2: ["dog grooming salon", "dog spa luxury", "pet grooming"],
        3: ["tibetan mastiff dog", "samoyed white dog", "rare breed dog"],
        4: ["dog show competition", "purebred championship", "dog award winner"],
        5: ["dog training obedience", "dog athlete agility", "working dog"],
        6: ["dog health care vet", "premium pet care", "dog nutrition"],
        7: ["dog mansion luxury home", "pet lifestyle rich", "dog owner wealthy"],
        8: ["dog love family", "loyal companion dog", "dog friendship"],
    },
}

# Fallback generic keywords
KEYWORDS_FALLBACK = {
    i: [f"lifestyle success {i}", f"motivation achievement", f"professional business"]
    for i in range(9)
}


def fetch_images(script: dict, config: dict) -> dict:
    api_key     = os.environ["PEXELS_API_KEY"]
    slug        = script["slug"]
    per_page    = config["pexels"]["per_page"]
    total_imgs  = config["video"]["images_per_video"]
    channel_key = config["channel"]["name"].lower().replace(" ", "")

    # Select keyword set for this channel
    keywords_map = KEYWORDS_BY_CHANNEL.get(channel_key, KEYWORDS_FALLBACK)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "images", slug)
    os.makedirs(out_dir, exist_ok=True)

    downloaded = []
    img_index  = 0
    headers    = {"Authorization": api_key}

    for chapter_num, keywords in keywords_map.items():
        for keyword in keywords:
            print(f"[image_fetch] Chapter {chapter_num} — '{keyword}'...")
            params = {
                "query":       keyword,
                "per_page":    per_page,
                "orientation": config["pexels"]["orientation"],
                "size":        config["pexels"]["size"],
            }
            try:
                resp = requests.get(PEXELS_API, headers=headers, params=params, timeout=15)
                resp.raise_for_status()
                photos = resp.json().get("photos", [])
            except Exception as e:
                print(f"[image_fetch] Warning: {e}")
                continue

            for photo in photos:
                url      = photo["src"].get("large2x") or photo["src"]["large"]
                filename = f"{img_index:04d}-ch{chapter_num:02d}-{photo['id']}.jpg"
                filepath = os.path.join(out_dir, filename)

                if not os.path.exists(filepath):
                    try:
                        img_data = requests.get(url, timeout=20).content
                        with open(filepath, "wb") as f:
                            f.write(img_data)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"[image_fetch] Download failed: {e}")
                        continue

                downloaded.append({"path": filepath, "chapter": chapter_num, "index": img_index})
                img_index += 1

            if img_index >= total_imgs:
                break
        if img_index >= total_imgs:
            break

    print(f"[image_fetch] Done — {len(downloaded)} images → {out_dir}")
    return {"images": downloaded, "directory": out_dir, "count": len(downloaded)}
