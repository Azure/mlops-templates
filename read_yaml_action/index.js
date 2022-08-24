const core = require('@actions/core');
const github = require('@actions/github');
const yaml = require('js-yaml');
const fs = require('fs');
checkGenerateEntity()

try {  
    const configData = core.getInput('config');
    fs.readFile(configData, 'utf8', (err, data) => {
    if (err) {
      console.error(err);
      return;
    }
    console.log(data);
    const SCHEMA = yaml.FAILSAFE_SCHEMA;
    const configYaml = yaml.load(data, { schema: SCHEMA }); 
    const namespace = String(configYaml["variables"]["namespace"]);
    const postfix = String(configYaml["variables"]["postfix"]);
    const environment = String(configYaml["variables"]["environment"]);
    var resource_group = String(configYaml["variables"]["resource_group"]);
    var aml_workspace = String(configYaml["variables"]["aml_workspace"]);
    if(checkGenerateEntity(resource_group)){
        resource_group = "rg-"+namespace+"-"+postfix+environment;
    }
    if(checkGenerateEntity(aml_workspace)){
        aml_workspace = "mlw-"+namespace+"-"+postfix+environment;
    }
    const batch_endpoint_name = "bep-"+namespace+"-"+postfix+environment;
    const online_endpoint_name = "oep-"+namespace+"-"+postfix+environment;
    core.setOutput("resource_group",resource_group);
    core.setOutput("aml_workspace", aml_workspace);
    core.setOutput("bep", batch_endpoint_name);
    core.setOutput("oep", online_endpoint_name);
  });
  
} catch (error) {
  core.setFailed(error.message);
}
function checkGenerateEntity(entity){
    let result = false;
    if (entity.includes("$")){
        result = true;
    }
    return result;
}
