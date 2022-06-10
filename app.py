from flask import Flask, render_template, jsonify, request, redirect, session, abort, flash
from flask_session import Session
from flask_pymongo import PyMongo
from passlib.hash import pbkdf2_sha256
import pymongo
import datetime
from flask_minify import minify