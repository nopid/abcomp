FROM nopid/walnut
RUN for i in Automata\ Library Command\ Files Macro\ Library Result Transducer\ Library Word\ Automata\ Library; do rm -rf "$i"; done
RUN mkdir ${HOME}/Command\ Files
RUN mkdir ${HOME}/notebooks/section4
ADD section4/out/*-abelian.tar.gz ${HOME}
ADD section3/out/abcomp.tar.xz ${HOME}
ADD section3/out/*_*.tar.xz ${HOME}
ADD ["section3/out/equi.tar.xz", "${HOME}/Word Automata Library"]
ADD ["section3/out/difffirst.tar.xz", "${HOME}/Word Automata Library"]
ADD ["section3/out/diffztri.tar.xz", "${HOME}/Word Automata Library"]
COPY notebooks ${HOME}/notebooks
COPY section4/out/*.zip ${HOME}/notebooks/section4
WORKDIR ${HOME}
USER root
RUN cd ${HOME}/Word\ Automata\ Library; rm *.log; for i in Equi*.txt; do mv $i D$(echo $i | tr '[:upper:]' '[:lower:]'); done
RUN cd ${HOME}/notebooks/section4; for i in *.zip; do unzip $i; done; rm *.zip
RUN find notebooks -iname '*.ipynb' | xargs jupyter trust 
RUN chown -R ${NB_UID} ${HOME}
USER ${USER}
