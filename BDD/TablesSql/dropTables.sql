DROP TABLE topic_wf CASCADE; 

DROP TABLE wf_nextflow CASCADE;

DROP TABLE contributor CASCADE; 

DROP TABLE person_git_comp CASCADE; 

DROP TABLE similarity_process CASCADE; 

DROP TABLE link_process_channel CASCADE;  

DROP TABLE link_channel_operation CASCADE;

DROP TABLE tools_have_topic CASCADE; 

DROP TABLE topic_tools CASCADE; 

DROP TABLE tool_in_workflow CASCADE; 

DROP TABLE tool_in_process CASCADE; 

DROP TABLE tools_have_in_out CASCADE; 

DROP TABLE in_out_data CASCADE; 

DROP TABLE tools_have_operation CASCADE;  

DROP TABLE operation_tool CASCADE; 

DROP TABLE tool CASCADE; 

DROP TABLE channel CASCADE; 

DROP TABLE operation_wf CASCADE; 

DROP TABLE process CASCADE; 

DROP TABLE workflow CASCADE; 

DROP TABLE person_git CASCADE; 

------------------------------------

drop type type_system CASCADE; 

drop type type_dsl;

drop type type_p CASCADE;

drop type type_kind; 

drop type type_c; 

drop type type_operation; 

------------------------------------

drop sequence seq_id_process;

drop sequence seq_id_wf;

drop sequence seq_id_channel;

drop sequence seq_id_operation_wf;

drop sequence seq_id_in_out_tool;

drop sequence seq_id_topic_tools;

drop sequence seq_id_operation_tools;