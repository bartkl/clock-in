#!/bin/bash

yad \
	--title "Clocker" \
	--window-icon "appointment" \
	--width 340 \
	--height 340 \
	--center \
	--text-info \
	--fontname "Monospace 10" \
	--filename hours.txt \
	--margins 12 \
	--buttons-layout center \
	--button Worked!emblem-default:0 \
	--button Slacked!weather:1
