/* REQUETES FINALES */
 
 /************************************************************************
 * Nombre de Workflow
 ************************************************************************
 */
 SELECT COUNT(id_wf) AS Nb_workflow
 FROM workflow ; 
 
 /************************************************************************
 * Workflow possédant le plus de forks
 ************************************************************************
 */
 SELECT name_wf AS Workflow, nb_forks
 FROM workflow 
 ORDER BY nb_forks DESC
 LIMIT 20;

 /************************************************************************
 * Workflow possédant le plus de stars
 ************************************************************************
 */
 SELECT name_wf AS Workflow, nb_stars
 FROM workflow 
 ORDER BY nb_stars DESC
 LIMIT 20;

 /************************************************************************
 * Workflow possédant le plus de forks+stars
 ************************************************************************
 */
 SELECT name_wf AS Workflow, ( nb_forks + nb_stars ) AS nb_forks_plus_stars
 FROM workflow 
 ORDER BY (nb_forks + nb_stars) DESC
 LIMIT 20;

 /************************************************************************
 * Workflow possédant le plus de watchers
 ************************************************************************
 */
 SELECT name_wf AS Workflow, nb_watchers
 FROM workflow 
 ORDER BY nb_watchers DESC
 LIMIT 20;

 /************************************************************************
 * Workflow possédant le plus de subscribers
 ************************************************************************
 */
 SELECT name_wf AS Workflow, nb_subscribers
 FROM workflow 
 ORDER BY nb_subscribers DESC
 LIMIT 20;

 /************************************************************************
 * Workflow possédant le plus de forks+stars+subscribers+watchers
 ************************************************************************
 */
 SELECT name_wf AS Workflow, ( nb_forks + nb_stars + nb_subscribers + nb_watchers ) AS nb_forks_stars_subs_watchers
 FROM workflow 
 ORDER BY (nb_forks + nb_stars + nb_subscribers + nb_watchers ) DESC
 LIMIT 20;

 /************************************************************************
 * Utilisation des workflows
 ************************************************************************
 */
 SELECT name_wf AS workflow, nb_forks,nb_stars, nb_subscribers, nb_watchers, (nb_forks + nb_stars + nb_subscribers + nb_watchers) AS Nb_total
 FROM workflow
 GROUP BY name_wf, nb_forks, nb_stars, nb_subscribers, nb_watchers
 ORDER BY Nb_total DESC
 LIMIT 50;

 /************************************************************************
 * Nombre total d'outils par workflow
 ************************************************************************
 */

 SELECT workflow.name_wf AS Workflow, COUNT(tool_in_workflow.url_biotools) AS Nb_total_tool
 FROM workflow, tool_in_workflow
 WHERE workflow.id_wf = tool_in_workflow.id_wf
 GROUP BY workflow.name_wf
 -- ORDER BY Nb_total_tool DESC
 LIMIT 50;

 /************************************************************************
 * Nombre d'outils differents par workflow
 ************************************************************************
 */

 SELECT workflow.name_wf AS Workflow, COUNT(DISTINCT(tool_in_workflow.url_biotools)) AS Nb_different_tool
 FROM workflow, tool_in_workflow
 WHERE workflow.id_wf = tool_in_workflow.id_wf
 GROUP BY workflow.name_wf
 -- ORDER BY Nb_different_tool DESC
 LIMIT 50;

 /************************************************************************
 * Nombre moyen d'utilisation d'outils par workflow
 ************************************************************************
 */

 SELECT ROUND(AVG(moyenne)) AS Moyenne_tools
 FROM ( SELECT workflow.name_wf AS Workflow, COUNT(tool_in_workflow.url_biotools) AS moyenne
        FROM workflow, tool_in_workflow
        WHERE workflow.id_wf = tool_in_workflow.id_wf
        GROUP BY workflow.name_wf) M; 

 /************************************************************************
 * Nombre de contributeur associé à un workflow
 ************************************************************************
 */

 SELECT workflow.name_wf AS Workflow, COUNT(DISTINCT(contributor.login_git)) AS Nb_contributor
 FROM workflow, contributor
 WHERE workflow.id_wf = contributor.id_wf
 GROUP BY workflow.name_wf
 ORDER BY Nb_contributor DESC
 LIMIT 50;

 /************************************************************************
 * Nombre de process par workflow
 ************************************************************************
 */

 SELECT workflow.name_wf AS Workflow, COUNT(process.id_wf) AS Nb_process
 FROM workflow, process
 WHERE workflow.id_wf = process.id_wf 
 GROUP BY workflow.name_wf
 ORDER BY Nb_process DESC 
 LIMIT 50;

 /************************************************************************
 * Nombre moyen de process par workflow
 ************************************************************************
 */

 SELECT ROUND(AVG(nb_process)) AS Moyenne_process
 FROM ( SELECT workflow.name_wf AS Workflow,COUNT(process.id_wf) AS nb_process
        FROM workflow, process
        WHERE workflow.id_wf = process.id_wf 
        GROUP BY workflow.name_wf) M ;

 /************************************************************************
 * Nombre de contributeur
 ************************************************************************
 */
 SELECT COUNT(login_git) AS Nb_contributor
 FROM person_git ; 

 /************************************************************************
 * Nombre de tools différents utilisés par créateurs 
 ************************************************************************
 */

SELECT contributor.login_git AS createur, COUNT(Nb_tools.tools_in_workflow) AS Nb_tools_used
FROM contributor, ( SELECT COUNT(DISTINCT(tool_in_workflow.url_biotools)) AS tools_in_workflow, workflow.id_wf AS id_workflow
                    FROM tool_in_workflow, workflow
                    WHERE tool_in_workflow.id_wf = workflow.id_wf
                    GROUP BY id_workflow) Nb_tools, workflow
WHERE contributor.login_git = workflow.login_owner_wf
AND workflow.id_wf = Nb_tools.id_workflow
GROUP BY contributor.login_git 
ORDER BY Nb_tools_used DESC
LIMIT 50;

 /************************************************************************
 * Nombre de contributions sur différents workflow par contributeur
 ************************************************************************
 */

 SELECT person_git.login_git, COUNT(contributor.id_wf) AS Nb_workflow
 FROM person_git, contributor
 WHERE person_git.login_git = contributor.login_git 
 GROUP BY person_git.login_git 
 ORDER BY Nb_workflow DESC
 LIMIT 50; 

 /************************************************************************
 * Nombre de particulier owner de workflow
 ************************************************************************
 */
 SELECT COUNT(person_git.login_git) AS nb_particular
 FROM person_git, workflow
 WHERE person_git.login_git = workflow.login_owner_wf
 AND person_git.login_git NOT IN (SELECT person_git_comp.login_git FROM person_git_comp) ;

 /************************************************************************
 * Nombre d'entreprise owner de workflow
 ************************************************************************
 */
 SELECT COUNT(person_git.login_git) AS nb_comp
 FROM person_git, person_git_comp, workflow
 WHERE person_git.login_git = workflow.login_owner_wf
 AND person_git.login_git = person_git_comp.login_git ;

 /************************************************************************
 * Nombre d'outils différents 
 ************************************************************************
 */
 SELECT COUNT(url_biotools) AS nb_tools
 FROM tool ;

 /************************************************************************
 * Nombre de process et de workflow dans lesquels l'outil est utilise
 ************************************************************************
 */

 SELECT tool.name_tool AS Tool, COUNT(tool_in_process.id_proc) AS Nb_process_use, COUNT(DISTINCT(tool_in_workflow.id_wf)) AS Nb_workflow_use
 FROM tool, tool_in_workflow, tool_in_process
 WHERE tool.url_biotools = tool_in_workflow.url_biotools
 AND tool.url_biotools = tool_in_process.url_biotools
 GROUP BY tool.name_tool
 ORDER BY Nb_workflow_use DESC
 LIMIT 50;

 /************************************************************************
 * Nom des topic Edam par outil
 ************************************************************************
 */

 SELECT tool.name_tool AS tools, topic_tools.term AS name_topic
 FROM tools_have_topic, topic_tools, tool
 WHERE tools_have_topic.id_topic = topic_tools.id_topic
 AND tools_have_topic.url_biotools = tool.url_biotools
 LIMIT 50 ;

 /************************************************************************
 * Nombre de topic Edam par outil
 ************************************************************************
 */
 SELECT tool.name_tool AS tools, COUNT(tools_have_topic.id_topic) AS nb_topic
 FROM tools_have_topic, tool
 WHERE tools_have_topic.url_biotools = tool.url_biotools
 GROUP BY tool.name_tool
 -- ORDER BY nb_topic DESC
 LIMIT 50;

 /************************************************************************
 * Nombre d'opération EDAM par outil
 ************************************************************************
 */
 SELECT tool.name_tool, COUNT(tools_have_operation.id_operation) AS nb_operation
 FROM tool, tools_have_operation
 WHERE tool.url_biotools = tools_have_operation.url_biotools
 GROUP BY tool.name_tool
 -- ORDER BY nb_operation DESC
 LIMIT 50;

 /************************************************************************
 * Nom des topics des outils utilisés dans un workflow
 ************************************************************************
 */
 SELECT workflow.name_wf AS workflow, topic_tools.term AS name_topic
 FROM workflow, topic_tools, tool_in_workflow, tools_have_topic
 WHERE workflow.id_wf = tool_in_workflow.id_wf
 AND tool_in_workflow.url_biotools = tools_have_topic.url_biotools
 AND tools_have_topic.id_topic = topic_tools.id_topic
 --GROUP BY workflow.name_wf
 LIMIT 50;

 /************************************************************************
 * Nombre d'inputs/outputs/inputs+outpus dans un process
 ************************************************************************
 */
 SELECT little_name AS "Name", nb_inputs, nb_outputs, (nb_inputs + nb_outputs) AS Nb_total
 FROM process
 GROUP BY little_name, nb_inputs, nb_outputs
 ORDER BY Nb_total DESC
 LIMIT 50;

 /************************************************************************
 * Nombre moyen d'inputs/outputs/inputs+outpus dans un process
 ************************************************************************
 */
 SELECT ROUND(AVG(moyenne.nb_inputs)) AS avg_inputs, ROUND(AVG(moyenne.nb_outputs)) AS avg_outputs, ROUND(AVG(moyenne.Nb_total)) AS avg_inputs_outputs
 FROM ( SELECT little_name AS "Name", nb_inputs, nb_outputs, (nb_inputs + nb_outputs) AS Nb_total
        FROM process
        GROUP BY little_name, nb_inputs, nb_outputs) moyenne ;

 /************************************************************************
 * Outils des process avec le plus d'inputs/outputs
 ************************************************************************
 */
 SELECT somme.little_name AS name_process, tool.name_tool, somme.Nb_total AS nb_inputs_outputs
 FROM (SELECT little_name, id_process, (nb_inputs + nb_outputs) AS Nb_total
       FROM process
       GROUP BY little_name, id_process) somme, tool_in_process, tool
 WHERE somme.id_process = tool_in_process.id_proc
 AND tool.url_biotools = tool_in_process.url_biotools
 ORDER BY somme.Nb_total DESC
 LIMIT 50;

 /************************************************************************
 * Nombre d'outils par process
 ************************************************************************
 */
 SELECT process.little_name AS process_name, COUNT(tool_in_process.url_biotools) as nb_tool_in_process
 FROM tool_in_process, process
 WHERE process.id_process = tool_in_process.id_proc
 GROUP BY process.little_name
 LIMIT 50;