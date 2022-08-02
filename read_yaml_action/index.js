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
    const configYaml = yaml.load(data, 'utf8');
    core.setOutput("resource_group", configYaml["variables"]["resource_group"]);
    core.setOutput("aml_workspace", configYaml["variables"]["aml_workspace"]);
  });
  
} catch (error) {
  core.setFailed(error.message);
}
