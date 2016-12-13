# coding=utf-8
import json
import logging

from django.conf import settings


class DebugLogMiddleware(object):
    
    logger = logging.getLogger('django')
    
    def process_response(self, request, response):
        try:
            self.logger.info("%s\n"
                "* VERSION: %s\n"
                "* PARAMS: \n\t%s\n",
                request.path,
                request.META.get('HTTP_APP_VERSION', 'UNKNOWN'),
                "\n\t".join(': '.join(kv) for kv in (set(request.POST.items()) | set(request.GET.items()))),
            )
        except:
            import traceback
            self.logger.critical(traceback.print_exc())

        try:
            resp_json = json.loads(response.content)
        except:
            pass
        else:
            if resp_json['status'] == 'error':
                self.logger.info('\n' + resp_json.get('msg', resp_json.get('error', 'error')))
            elif settings.RESPONSE_LOG:
                self.logger.info(json.dumps(resp_json, ensure_ascii=False, indent=4))
        return response