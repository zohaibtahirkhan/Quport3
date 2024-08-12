from rest_framework.views import APIView
from .models import Model
import os


class QuPortChatbotView(APIView):
    def post(self, request):
        files_path = []
        directory = '/home/zohaib/PycharmProjects/pythonProject/bot/chatbot/documents/'
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                files_path.append(full_path)

        bot = Model(files_path)
        res = bot.chat(request)
        return res


class PadelChatbotView(APIView):
    def post(self, request):
        files = []
        directory = '/home/zohaib/PycharmProjects/pythonProject/bot/chatbot/documents/padel_documents/'
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isfile(full_path):
                files.append(full_path)

        bot = Model(files)
        res = bot.chat(request)
        return res


class SoccerChatbotView(APIView):
    def post(self, request):
        files = []
        directory = '/home/zohaib/PycharmProjects/pythonProject/bot/chatbot/documents/soccer_documents/'
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isfile(full_path):
                files.append(full_path)

        bot = Model(files)
        res = bot.chat(request)
        return res


class BakermanChatbotView(APIView):
    def post(self, request):
        files = []
        directory = '/home/zohaib/PycharmProjects/pythonProject/bot/chatbot/documents/bakerman_documents/'
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isfile(full_path):
                files.append(full_path)

        bot = Model(files)
        res = bot.chat(request)
        return res
