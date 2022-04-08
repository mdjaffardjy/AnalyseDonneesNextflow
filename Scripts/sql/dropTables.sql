drop table topic_wf CASCADE;

drop table workflow CASCADE;

drop table person_git CASCADE;

drop table person_git_comp CASCADE;

drop table contributor CASCADE;

drop table process CASCADE;

drop table similarity_process CASCADE;

drop table channel CASCADE;

drop table operation_wf CASCADE;

drop table channel_have_operation CASCADE;

drop table tool CASCADE;

drop table tool_comp CASCADE;

drop table topic_tools CASCADE;

drop table tool_in_workflow CASCADE;

drop table tool_in_process CASCADE;

drop table tools_have_topic CASCADE;

drop table operation_tool CASCADE;

drop table tools_have_operation CASCADE;

drop table credit_tool CASCADE;

drop table credit_tool_comp CASCADE;

drop table in_out_data CASCADE;

drop table in_out_format CASCADE;

drop table in_out_link_data_format CASCADE;

drop table tools_have_in_out CASCADE;

drop table tools_contact_credit CASCADE;

drop table process_have_channel CASCADE;

drop table collectionID CASCADE;

------------------------------------

drop type type_system CASCADE;

drop type type_p CASCADE;

drop type type_accessibility CASCADE;

drop type type_elixirNode CASCADE;

drop type type_elixirPlatform CASCADE;

drop type type_entity;

drop type type_role;

drop type type_kind;

drop type type_c;

drop type type_operation;

drop type type_license_tool;

------------------------------------

drop sequence seq_id_process;

drop sequence seq_id_wf;

drop sequence seq_id_channel;

drop sequence seq_id_operation_wf;

drop sequence seq_id_in_out_tool;

drop sequence seq_id_credit;

drop sequence seq_id_topic_tools;

drop sequence seq_id_operation_tools;

drop sequence seq_id_in_out_tool_format;