 /************************************************************************
 * Nom des topics des outils utilisés dans un workflow
 ************************************************************************
 */
 SELECT workflow.name_wf AS workflow, topic_tools.term AS name_topic
 FROM workflow, topic_tools, tool_in_workflow, tools_have_topic
 WHERE workflow.id_wf = tool_in_workflow.id_wf
 AND tool_in_workflow.url_biotools = tools_have_topic.url_biotools
 AND tools_have_topic.id_topic = topic_tools.id_topic
 AND workflow.id_wf = 894;