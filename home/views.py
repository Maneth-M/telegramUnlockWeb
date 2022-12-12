from django.shortcuts import render, HttpResponse
from telethon import TelegramClient, sync
from .config import Config
from django.http import Http404


async def index(request):

    phone = request.POST.get("phone")
    code = request.POST.get("code")
    phone_code_hash = request.POST.get("phone_code_hash")
    error = ""

    if phone:
        client = TelegramClient(f"sessions/{phone}", Config.api_id, Config.api_hash)
        await client.connect()
    if phone and not code:
        phone_code_hash = await client.send_code_request(phone)
        phone_code_hash = phone_code_hash.phone_code_hash
    if phone and code:
        try:
            await client.sign_in(phone, code=code, phone_code_hash=phone_code_hash)
            await client.disconnect()
            file_path = f"sessions/{phone}.session"
            try:
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + f"{phone}.session"
                    return response

            except:
                raise Http404
        except Exception as e:
            print(e)
            error = "Invalid Code"

    payload = {
        "phone": phone,
        "phone_code_hash": phone_code_hash,
        "errors": error
    }

    return render(request, "base.html", context=payload)
