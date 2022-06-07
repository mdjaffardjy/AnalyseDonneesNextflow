/************************************************************************
 * Table Arrete : 
 ************************************************************************
 */
CREATE TYPE type_noeud AS ENUM ('process', 'operation','beginning', 'end');

CREATE TABLE arete (
    id_channel INT,             -- id of the channel
    id_output INT,              -- id of the output node
    type_output type_noeud,      -- type of the output node
    id_input INT,               -- id of the input node
    type_input type_noeud,     -- type of the input node
    id_wf INT,                  -- id of the wf

    CONSTRAINT pk_arete PRIMARY KEY (id_channel,id_wf),
    CONSTRAINT fk_arete_w FOREIGN KEY (id_wf) REFERENCES workflow(id_wf),
    CONSTRAINT fk_arete_c FOREIGN KEY (id_channel) REFERENCES channel(id_channel)
);
