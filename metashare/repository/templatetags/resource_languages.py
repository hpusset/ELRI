from django import template

from metashare.repository.models import corpusInfoType_model, \
    toolServiceInfoType_model, lexicalConceptualResourceInfoType_model, \
    languageDescriptionInfoType_model

register = template.Library()

class ResourceLanguages(template.Node):
    """
    Template tag that allows to display languages in result page template.    
    """
    
    def __init__(self, context_var):
        """
        Initialises this template tag.
        """
        super(ResourceLanguages, self).__init__()
        self.context_var = template.Variable(context_var)
        
    def render(self, context):
        """
        Renders languages.
        """
        result = []
        corpus_media = self.context_var.resolve(context)
    
        if isinstance(corpus_media, corpusInfoType_model):
            media_type = corpus_media.corpusMediaType
            for corpus_info in media_type.corpustextinfotype_model_set.all():
                result.extend([lang.languageName for lang in
                               corpus_info.languageinfotype_model_set.all()])

        elif isinstance(corpus_media, lexicalConceptualResourceInfoType_model):
            lcr_media_type = corpus_media.lexicalConceptualResourceMediaType
            if lcr_media_type.lexicalConceptualResourceTextInfo:
                result.extend([lang.languageName for lang in lcr_media_type \
                        .lexicalConceptualResourceTextInfo.languageinfotype_model_set.all()])

        elif isinstance(corpus_media, languageDescriptionInfoType_model):
            ld_media_type = corpus_media.languageDescriptionMediaType
            if ld_media_type.languageDescriptionTextInfo:
                result.extend([lang.languageName for lang in ld_media_type \
                            .languageDescriptionTextInfo.languageinfotype_model_set.all()])

        elif isinstance(corpus_media, toolServiceInfoType_model):
            if corpus_media.inputInfo:
                result.extend(l.languageName for l in corpus_media.inputInfo.languagesetinfotype_model_set.all())
            if corpus_media.outputInfo:
                result.extend(l.languageName for l in corpus_media.outputInfo.languagesetinfotype_model_set.all())

        result = list(set(result))
        result.sort()

        return u"".join(u"<li class=\"languages\">{}</li>".format(lang) for lang in result)

def resource_languages(parser, token):
    """
    Use it like this: {% load_languages object.resourceComponentType.as_subclass %}
    """
    tokens = token.contents.split()
    if len(tokens) != 2:
        _msg = "%r tag accepts exactly two arguments" % tokens[0]
        raise template.TemplateSyntaxError(_msg)
    
    return ResourceLanguages(tokens[1])


register.tag('resource_languages', resource_languages)
