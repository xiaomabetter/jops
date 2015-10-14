#!/bin/bash -x

#gem install --pre asciidoctor-diagram
#gem install --pre asciidoctor

bundle exec asciidoctor -n -r asciidoctor-diagram operation-manual.asc -D ../


#asciidoctor-pdf-cjk-kai_gen_gothic-install
#/Users/lax/.rvm/gems/ruby-2.2.1/gems/asciidoctor-pdf-cjk-kai_gen_gothic-0.1.0/data/fonts/RobotoMono-Regular.ttf not found
#curl https://github.com/akiratw/kaigen-gothic/archive/v1.004.20150912.tar.gz -L -O

#bundle exec asciidoctor -n -s -r asciidoctor-pdf -r asciidoctor-diagram -r asciidoctor-pdf-cjk-kai_gen_gothic -a pdf-style=KaiGenGothicCN operation-manual.asc -b pdf

#bundle exec asciidoctor -r asciidoctor-pdf -r asciidoctor-diagram -r asciidoctor-pdf-cjk-kai_gen_gothic -b pdf operation-manual.asc
#bundle exec asciidoctor -r asciidoctor-pdf -r asciidoctor-diagram -b pdf operation-manual.asc

asciidoctor -r asciidoctor-pdf -r asciidoctor-diagram -r asciidoctor-pdf-cjk-kai_gen_gothic -b pdf -s -t -q -D ../ operation-manual.asc
