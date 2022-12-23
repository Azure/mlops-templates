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
        
    // TODO Verify if variables do not exist or are empty
    const namespace = String(configYaml["variables"]["namespace"]);
    const postfix = String(configYaml["variables"]["postfix"]);
    const environment = String(configYaml["variables"]["environment"]);
    var enable_aml_computecluster = Boolean(configYaml["variables"]["enable_aml_computecluster"]);
    var enable_monitoring = Boolean(configYaml["variables"]["enable_monitoring"]);
    var resource_group = String(configYaml["variables"]["resource_group"]);
    var location = String(configYaml["variables"]["location"]);
    var aml_workspace = String(configYaml["variables"]["aml_workspace"]);

    var terraform_version = String(configYaml["variables"]["terraform_version"]);
    var terraform_workingdir = String(configYaml["variables"]["terraform_workingdir"]);
    var terraform_st_location = String(configYaml["variables"]["terraform_st_location"]);
    var terraform_st_resource_group = String(configYaml["variables"]["terraform_st_resource_group"]);
    var terraform_st_storage_account = String(configYaml["variables"]["terraform_st_storage_account"]);
    var terraform_st_container_name = String(configYaml["variables"]["terraform_st_container_name"]);
    var terraform_st_key = String(configYaml["variables"]["terraform_st_key"]);

    if(checkGenerateEntity(terraform_st_location)){
      terraform_st_location = location;
    }
    if(checkGenerateEntity(resource_group)){
        resource_group = "rg-"+namespace+"-"+postfix+environment;
    }
    if(checkGenerateEntity(aml_workspace)){
        aml_workspace = "mlw-"+namespace+"-"+postfix+environment;
    }

    if(checkGenerateEntity(terraform_st_resource_group)){
      terraform_st_resource_group = "rg-"+namespace+"-"+postfix+environment+"-tf";
    }
    if(checkGenerateEntity(terraform_st_storage_account)){
      terraform_st_storage_account = "st"+namespace+postfix+environment+"tf";
    }

    const batch_endpoint_name = "bep-"+namespace+"-"+postfix+environment;
    const online_endpoint_name = "oep-"+namespace+"-"+postfix+environment;
    core.setOutput("location",location);
    core.setOutput("namespace",namespace);
    core.setOutput("postfix",postfix);
    core.setOutput("environment",environment);
    core.setOutput("enable_monitoring",enable_monitoring);
    core.setOutput("enable_aml_computecluster",enable_aml_computecluster);
    core.setOutput("resource_group",resource_group);
    core.setOutput("aml_workspace", aml_workspace);
    core.setOutput("bep", batch_endpoint_name);
    core.setOutput("oep", online_endpoint_name);
    core.setOutput("terraform_version", terraform_version);
    core.setOutput("terraform_workingdir", terraform_workingdir);
    core.setOutput("terraform_st_location", terraform_st_location);
    core.setOutput("terraform_st_resource_group", terraform_st_resource_group);
    core.setOutput("terraform_st_storage_account", terraform_st_storage_account);
    core.setOutput("terraform_st_container_name", terraform_st_container_name);
    core.setOutput("terraform_st_key", terraform_st_key);
  });
  
} catch (error) {
  core.setFailed(error.message);
}
function checkGenerateEntity(entity){
    var result = false;
    var entityStr = String(entity);
    if (entityStr.includes("$")){
        result = true;
    }
    return result;
}
