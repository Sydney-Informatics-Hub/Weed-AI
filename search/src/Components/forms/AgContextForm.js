import React, { Component } from 'react'
import { Helmet } from "react-helmet";
import { withRouter } from 'react-router-dom';
import agcontextSchema from '../../Schemas/AgContext.json'
import Container from '@material-ui/core/Container';
import Box from '@material-ui/core/Box';
import renderers from '../formRenderers/default_renderers';
import { createAjv } from '@jsonforms/core';
import { JsonForms } from '@jsonforms/react';
import UploadJsonButton from './UploadJsonButton';
import { materialCells } from '@jsonforms/material-renderers';

const uischema = {
  "type": "Categorization",
  "elements": [
    {
      "type": "Category",
      "label": "The Crop",
      "elements": [
        {
          "type": "Control",
          "scope": "#/properties/crop_type"
        },
        {
          "type": "Control",
          "label": "BBCH Growth Stage",
          "scope": "#/properties/bbch_growth_range"
        },
        {
          "type": "Control",
          "scope": "#/properties/soil_colour"
        },
        {
          "type": "Control",
          "scope": "#/properties/surface_cover"
        },
        {
          "type": "Control",
          "scope": "#/properties/surface_coverage"
        },
        {
          "type": "HorizontalLayout",
          "elements": [
            {
              "type": "Control",
              "scope": "#/properties/location_lat"
            },
            {
              "type": "Control",
              "scope": "#/properties/location_long"
            }
          ]
        }
      ]
    },
    {
      "type": "Category",
      "label": "The Photography",
      "elements": [
        {
          "type": "Control",
          "scope": "#/properties/camera_make"
        },
        {
          "type": "Control",
          "scope": "#/properties/camera_lens"
        },
        {
          "type": "Control",
          "scope": "#/properties/camera_lens_focallength"
        },
        {
          "type": "Control",
          "scope": "#/properties/camera_height"
        },
        {
          "type": "Control",
          "scope": "#/properties/camera_angle"
        },
        {
          "type": "Control",
          "scope": "#/properties/camera_fov"
        },
        {
          "type": "Control",
          "scope": "#/properties/ground_speed"
        },
        {
          "type": "Control",
          "scope": "#/properties/lighting"
        },
        {
          "type": "Control",
          "scope": "#/properties/photography_description",
          "options": {"multi": true}
        }
      ]
    },
    {
      "type": "Category",
      "label": "Other Details",
      "elements": [
        {
          "type": "Control",
          "scope": "#/properties/cropped_to_plant"
        },
        {
          "type": "Control",
          "scope": "#/properties/emr_channels"
        },
        {
          "type": "Control",
          "scope": "#/properties/weather_description",
          "options": {"multi": true}
        }
      ]
    }
  ]
};

class AgContextForm extends Component {
    constructor(props) {
        super(props);
        this.state = {formData: this.props.formData};
    }

    render() {
        const schema = agcontextSchema;

        return (
            <JsonForms
              schema={schema}
              uischema={uischema}
              data={this.props.formData}
              renderers={renderers}
              cells={materialCells}
              ajv = {createAjv({
                useDefaults: true,
                formats: {
                  'plant_species': {test: x => true},  // bypass validation for now
                },
              })}
              onChange={e => {
                  if (this.props.handleValidation){
                    this.props.handleValidation('agcontexts', e.errors.length === 0);
                  }
                  this.setState({formData: e.data});
                  if (this.props.onChange) {
                      e.formData = e.data;
                      e.formData["id"] = 0;
                      this.props.onChange(e);
                  }
              }}
            />
        );
    }
}


class StandaloneEditor extends Component {
    constructor(props) {
        super(props);
        this.state = {formData: this.props.formData || {} }
    }
    render() {
        return (
            <Container maxWidth="sm">
                <Helmet>
                    <title>AgContext Editor - Weed-AI</title>
                    <meta name="description" content="Edit and save the agricultural and photographic context of your annotated image collection." />
                </Helmet>
                <h2>AgContext Editor</h2>
                <Box boxShadow={3} px={2} py={1} my={2}>
                    <AgContextForm formData={this.state.formData} onChange={e => this.setState({formData: e.formData})} />
                </Box>
                <UploadJsonButton initialValue={this.state.formData} downloadName="agcontext" onClose={(value) => {this.setState({formData: value})}} />
            </Container>
        );
    }
}


export default AgContextForm;
export const Standalone = withRouter(StandaloneEditor);
