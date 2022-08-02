const core = require('@actions/core');
const github = require('@actions/github');
const yaml = require('js-yaml');
const fs = require('fs');
try {  
    const configData = core.getInput('config');
    fs.readFile(configData, 'utf8', (err, data) => {
    if (err) {
      console.error(err);
      return;
    }
    console.log(data);
    const SCHEMA = yaml.FAILSAFE_SCHEMA
    const configYaml = yaml.load(data, { schema: SCHEMA }); 
    const namespace = String(configYaml["variables"]["namespace"])
    const postfix = String(configYaml["variables"]["postfix"])
    const environment = String(configYaml["variables"]["environment"])
    const resource_group = "rg-"+namespace+"-"+postfix+environment
    const aml_workspace = "mlw-"+namespace+"-"+postfix+environment
    core.setOutput("resource_group",resource_group);
    core.setOutput("aml_workspace", aml_workspace);
  });
  
} catch (error) {
  core.setFailed(error.message);
}
