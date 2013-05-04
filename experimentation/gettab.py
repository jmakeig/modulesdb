#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

tabid = 0
asdf = subprocess.check_call('./gettab.sh', stdout=tabid)
