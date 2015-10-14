#!/bin/bash

#gem install --pre asciidoctor-diagram
#gem install --pre asciidoctor

asciidoctor -n -r asciidoctor-diagram operation-manual.asc -D ./output/

#asciidoctor-pdf-cjk-kai_gen_gothic-install
asciidoctor-pdf -n -r asciidoctor-diagram -r asciidoctor-pdf-cjk-kai_gen_gothic -a pdf-style=KaiGenGothicCN operation-manual.asc -D ./output/

#/Users/lax/.rvm/gems/ruby-2.2.1/gems/asciidoctor-pdf-cjk-kai_gen_gothic-0.1.0/data/fonts/RobotoMono-Regular.ttf not found
#curl https://github.com/akiratw/kaigen-gothic/archive/v1.004.20150912.tar.gz -L -O
