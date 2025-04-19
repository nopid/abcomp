FROM nopid/walnut
RUN for i in Automata\ Library Command\ Files Macro\ Library Result Transducer\ Library Word\ Automata\ Library; do rm -rf "$i"; done
RUN mkdir ${HOME}/Command\ Files
RUN mkdir ${HOME}/notebooks/section4
ADD section4/out/*-abelian.tar.gz ${HOME}
ADD section3/out/abcomp.tar.xz ${HOME}
ADD section3/out/*_*.tar.xz ${HOME}
COPY section4/out/*.zip ${HOME}/notebooks/section4
RUN cd ${HOME}/notebooks/section4; for i in *.zip; do unzip $i; done; rm *.zip
WORKDIR ${HOME}
USER root
RUN jupyter trust notebooks/*.ipynb
RUN chown -R ${NB_UID} ${HOME}
USER ${USER}
