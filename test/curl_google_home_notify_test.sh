#!/bin/bash
curl -v -s -X POST http://localhost:5000/makeNotify -H "Content-Type: application/json" -d '{"text":"abc"}'
echo

exit 0
