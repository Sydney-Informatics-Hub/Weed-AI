import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import UploaderSingle from './uploader_single';
import UploaderImages from './uploader_images';
import CategoryMapper from './uploader_category_mapper';
import ErrorMessage from '../error/display';
import AgContextForm from '../forms/AgContextForm';
import UploadJsonButton from '../forms/UploadJsonButton';
import MetadataForm from '../forms/MetadataForm';
import axios from 'axios';
import Cookies from 'js-cookie';
import cloneDeep from 'lodash/cloneDeep';


const baseURL = new URL(window.location.origin);

const useStyles = (theme) => ({
  root: {
    width: '100%',
  },
  button: {
    marginRight: theme.spacing(1),
  },
  instructions: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
});

const stepsByType = {
    "coco": [
        {title: "Upload Coco", type: "coco-upload"},
        {title: "Categories", type: "categories"},
        {title: "Add Agcontext", type: "agcontext"},
        {title: "Add Metadata", type: "metadata"},
        {title: "Upload Images", type: "images"}
    ],
    "weedcoco": [
        {title: "Upload Weedcoco", type: "weedcoco-upload"},
        {title: "Upload Images", type: "images"}
    ]
}

class UploadStepper extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            activeStep: 0,
            skip_mapping: {'weedcoco': -1, 'coco': -1},
            skipped: new Set(),
            steps: stepsByType[this.props.upload_type].map(step => step.title),
            upload_id: 0,
            images: [],
            categories: [],
            imageReady: false,
            ag_context: {},
            metadata: {},
            category_status: false,
            coco_form_validation: {'agcontexts': false, 'metadata': false},
            error_message: "init",
            error_message_details: "",
        }
        this.isStepOptional = this.isStepOptional.bind(this);
        this.isStepSkipped = this.isStepSkipped.bind(this);
        this.handleUploadId = this.handleUploadId.bind(this);
        this.handleImages = this.handleImages.bind(this);
        this.handleCategories = this.handleCategories.bind(this);
        this.handleImageReady = this.handleImageReady.bind(this);
        this.handleUpdateCategories = this.handleUpdateCategories.bind(this);
        this.handleAgContextsFormData = this.handleAgContextsFormData.bind(this);
        this.handleMetadataFormData = this.handleMetadataFormData.bind(this);
        this.handleErrorMessage = this.handleErrorMessage.bind(this);
        this.handleNext = this.handleNext.bind(this);
        this.handleBack = this.handleBack.bind(this);
        this.handleSkip = this.handleSkip.bind(this);
        this.handleReset = this.handleReset.bind(this);
        this.handleUploadAgcontexts = this.handleUploadAgcontexts.bind(this);
        this.handleUploadMetadata = this.handleUploadMetadata.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleCategoryStatus = this.handleCategoryStatus.bind(this);
        this.isNextEnabled = this.isNextEnabled.bind(this);
        this.handleValidation = this.handleValidation.bind(this);
        this.getStepContent = this.getStepContent.bind(this);
    }

    isStepOptional(step, upload_type) {
        return this.state.skip_mapping[upload_type] === step;
    };

    isStepSkipped(step) {
        return this.state.skipped.has(step);
    };

    handleUploadId(upload_id) {
        this.setState({upload_id: upload_id});
    }

    handleImages(images) {
        this.setState({images: images});
    }

    handleCategories(categories) {
        this.setState({categories: cloneDeep(categories)});
    }

    handleImageReady(imageReady) {
        this.setState({imageReady: imageReady});
    }

    handleAgContextsFormData(formData) {
        this.setState({ag_context: formData});
    }

    handleMetadataFormData(formData) {
        this.setState({metadata: formData});
    }

    handleErrorMessage(message, details="") {
        this.setState({error_message: message, error_message_details: details});
    }

    handleNext() {
        if (this.state.activeStep === this.state.steps.length - 1){
            this.handleSubmit();
            this.props.handleClose();
            this.handleReset();
        }
        else {
            let newSkipped = this.state.skipped;
            let activeStep = this.state.activeStep;
            if (this.isStepSkipped(activeStep)) {
                newSkipped = new Set(newSkipped.values());
                newSkipped.delete(activeStep);
            }
            this.setState(prevState => {return {activeStep: prevState.activeStep + 1}});
            this.setState({skipped: newSkipped});
            this.handleErrorMessage("init")
        }
    };

    handleBack(){
        this.setState(prevState => {return {activeStep: prevState.activeStep - 1}});
        this.handleErrorMessage("init")
    };

    handleSkip(){
        if (!this.isStepOptional(this.state.activeStep, this.props.upload_type)) {
            // You probably want to guard against something like this,
            // it should never occur unless someone's actively trying to break something.
            throw new Error("You can't skip a step that isn't optional.");
        }
        this.setState(prevState => {return {activeStep: prevState.activeStep + 1}});
        this.setState(prevState => {
            const newSkipped = new Set(prevState.skipped.values());
            newSkipped.add(this.state.activeStep);
            return {skipped: newSkipped};
        })
    };

    handleReset(){
        this.setState({activeStep: 0})
    };

    handleUpdateCategories(){
        axios({
            method: 'post',
            url: baseURL + "api/update_categories/",
            data: {
                "upload_id": this.state.upload_id,
                "categories": this.state.categories
            },
            headers: {'X-CSRFToken': Cookies.get('csrftoken') }
        }).then(res => {
            console.log(res)
            this.handleErrorMessage("")
            this.handleNext()
        })
        .catch(err => {
            console.log(err)
            this.handleErrorMessage("Invalid categories input")
        })
    }

    handleUploadAgcontexts(){
        axios({
            method: 'post',
            url: baseURL + "api/upload_agcontexts/",
            data: {
                "upload_id": this.state.upload_id,
                "ag_contexts": this.state.ag_context
            },
            headers: {'X-CSRFToken': Cookies.get('csrftoken') }
        }).then(res => {
            console.log(res)
            this.handleErrorMessage("")
            this.handleNext()
        })
        .catch(err => {
            console.log(err)
            this.handleErrorMessage("Invalid input for AgContext")
        })
    }

    handleUploadMetadata(){
        axios({
            method: 'post',
            url: baseURL + "api/upload_metadata/",
            data: {
                "upload_id": this.state.upload_id,
                "metadata": this.state.metadata
            },
            headers: {'X-CSRFToken': Cookies.get('csrftoken') }
        }).then(res => {
            console.log(res)
            this.handleErrorMessage("")
            this.handleNext()
        })
        .catch(err => {
            console.log(err)
            this.handleErrorMessage("Failed to submit metadata")
        })
    }

    handleSubmit(){
        const baseURL = new URL(window.location.origin);
        const body = new FormData()
        body.append('upload_id', this.state.upload_id)
        axios({
            method: 'post',
            url: baseURL + "api/submit_deposit/",
            data: body,
            headers: {'Content-Type': 'multipart/form-data', 'X-CSRFToken': Cookies.get('csrftoken') }
        })
    }

    handleValidation(formKey, status){
        this.setState(prevState => {
            const newState = {coco_form_validation: {...prevState.coco_form_validation}}
            newState.coco_form_validation[formKey] = status
            return newState
        })
    }

    handleCategoryStatus(category_status){
        this.setState({category_status: category_status})
    }

    isNextEnabled(){
        if (this.state.activeStep === 1) {
            return this.props.upload_type === 'coco' && this.state.category_status && 'categories'
        } else if (this.state.activeStep == 2) {
            return this.props.upload_type === 'coco' && this.state.coco_form_validation['agcontexts'] && 'agcontexts'
        } else if (this.state.activeStep === 3) {
            return this.props.upload_type === 'coco' && this.state.coco_form_validation['metadata'] && 'metadata'
        } else {
            return false
        }
    }

    getStepContent() {
        const step = stepsByType[this.props.upload_type][this.state.activeStep].type
        switch (step) {
            case "coco-upload":
            case "weedcoco-upload":
                const schema = step == "coco-upload" ? "compatible-coco" : "weedcoco"
                return <UploaderSingle upload_id={this.state.upload_id} images={this.state.images} handleUploadId={this.handleUploadId} handleImages={this.handleImages} handleCategories={this.handleCategories} handleErrorMessage={this.handleErrorMessage} schema={schema}/>
            case "categories":
                return <CategoryMapper categories={cloneDeep(this.state.categories)} handleCategories={this.handleCategories} handleCategoryStatus={this.handleCategoryStatus} handleErrorMessage={this.handleErrorMessage}/>
            case "agcontext":
                return (
                    <React.Fragment>
                        <AgContextForm formData={this.state.ag_context} handleValidation={this.handleValidation} onChange={e => {
                            this.handleAgContextsFormData(e.formData)
                            this.handleErrorMessage("init")
                        }} />
                        <UploadJsonButton initialValue={this.state.ag_context} downloadName="agcontext" onClose={(value) => {this.handleAgContextsFormData(value)}} />
                    </React.Fragment>
                )
            case "metadata":
                return (
                    <React.Fragment>
                        <MetadataForm formData={this.state.metadataFormData} handleValidation={this.handleValidation} onChange={e => {
                            this.handleMetadataFormData(e.formData)
                            this.handleErrorMessage("init")
                        }} />
                        <UploadJsonButton initialValue={this.state.metadata} downloadName="dataset-meta" onClose={(value) => {this.handleMetadataFormData(value)}} />
                    </React.Fragment>
                )
            case "images":
                return <UploaderImages upload_id={this.state.upload_id} images={this.state.images} handleImageReady={this.handleImageReady} handleErrorMessage={this.handleErrorMessage}/>
            default:
                return ''
        }
    }

    render(){
        const { classes } = this.props;
        return (
            <div className={classes.root}>
            <Stepper activeStep={this.state.activeStep}>
                {this.state.steps.map((label, index) => {
                const stepProps = {};
                const labelProps = {};
                if (this.isStepOptional(index, this.props.upload_type)) {
                    labelProps.optional = <Typography variant="caption">Optional</Typography>;
                }
                if (this.isStepSkipped(index)) {
                    stepProps.completed = false;
                }
                return (
                    <Step key={label} {...stepProps}>
                    <StepLabel {...labelProps}>{label}</StepLabel>
                    </Step>
                );
                })}
            </Stepper>
            <div>
                <Typography className={classes.instructions}>
                    {this.getStepContent()}
                </Typography>
                <ErrorMessage error={this.state.error_message} details={this.state.error_message_details}/>
                <div>
                    <Button disabled={this.state.activeStep === 0} onClick={this.handleBack} className={classes.button}>
                        Back
                    </Button>
                    {this.isStepOptional(this.state.activeStep, this.props.upload_type)
                    && (
                        <Button
                        variant="contained"
                        color="primary"
                        onClick={this.handleSkip}
                        className={classes.button}
                        disabled={this.state.error_message.length > 0 && this.state.error_message !== "init"}
                        >
                        Skip
                        </Button>
                    )}
        
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={this.isNextEnabled() === 'categories' ? this.handleUpdateCategories : this.isNextEnabled() === 'agcontexts' ? this.handleUploadAgcontexts : this.isNextEnabled() === 'metadata' ? this.handleUploadMetadata : this.handleNext}
                        className={classes.button}
                        disabled={this.state.error_message.length > 0 &&
                                  (this.state.activeStep !== this.state.steps.length - 1 ||
                                  this.state.activeStep === this.state.steps.length - 1 && !this.state.imageReady) &&
                                  !this.isNextEnabled()}
                    >
                        {this.state.activeStep === this.state.steps.length - 1 ? 'Submit' : 'Next'}
                    </Button>
                </div>
            </div>
            </div>
        );
    }
};

export default withStyles(useStyles)(UploadStepper);

