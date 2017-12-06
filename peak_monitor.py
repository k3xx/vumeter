# See http://freshfoo.com/blog/pulseaudio_monitoring for information on how
# this module works.

import sys
from Queue import Queue
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast

# From https://github.com/Valodim/python-pulseaudio
from pulseaudio.lib_pulseaudio import *

class PeakMonitor(object):

    def __init__(self, sink_name, rate):
        self.sink_name = sink_name
        self.rate = rate

        # Wrap callback methods in appropriate ctypefunc instances so
        # that the Pulseaudio C API can call them
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        self._server_info_cb = pa_server_info_cb_t(self.server_info_cb)
        self._sink_info_cb = pa_sink_info_cb_t(self.sink_info_cb)
        self._stream_read_cb = pa_stream_request_cb_t(self.stream_read_cb)
        self._update_cb = pa_context_subscribe_cb_t(self.update_cb)
        self._success_cb = pa_context_success_cb_t(self.success_cb)
        

        # stream_read_cb() puts peak samples into this Queue instance
        self._samples = Queue()

        # Create the mainloop thread and set our context_notify_cb
        # method to be called when there's updates relating to the
        # connection to Pulseaudio
        _mainloop = pa_threaded_mainloop_new()
        _mainloop_api = pa_threaded_mainloop_get_api(_mainloop)
        context = pa_context_new(_mainloop_api, 'peak_demo')
        pa_context_set_state_callback(context, self._context_notify_cb, None)
        pa_context_connect(context, None, 0, None)
        pa_threaded_mainloop_start(_mainloop)

    def __iter__(self):
        while True:
            yield self._samples.get()
            self._samples.task_done()

    
    def request_update(self, context):
        #Requests a sink info update (sink_info_cb is called)
        
        pa_operation_unref(pa_context_get_sink_info_by_name(
            context, self.sink_name, self._sink_info_cb, None))

    def success_cb(self, context, success, userdata):
        pass
    
    def update_cb(self, context, t, idx, userdata):
        #A sink property changed, calls request_update
        self.request_update(context)
    
    def server_info_cb(self, context, server_info_p, userdata):
        #Retrieves the default sink and calls request_update
        server_info = server_info_p.contents
        self.sink_name = server_info.default_sink_name
        self.request_update(context)

    def context_notify_cb(self, context, _):
        state = pa_context_get_state(context)

        if state == PA_CONTEXT_READY:
            print "Pulseaudio connection ready..."
            # Connected to Pulseaudio. Now request that sink_info_cb
            # be called with information about the available sinks.
            o = pa_context_get_sink_info_list(context, self._sink_info_cb, None)
            pa_operation_unref(o)

            # This starts a pulse instant, which might be unwanted (and leads to bad performance for my configuration with mopidy)
            #pa_operation_unref(pa_context_get_server_info(context, self._server_info_cb, None))
            #pa_context_set_subscribe_callback(context, self._update_cb, None)
            #pa_operation_unref(pa_context_subscribe(context, PA_SUBSCRIPTION_EVENT_CHANGE | PA_SUBSCRIPTION_MASK_SINK, self._success_cb, None))

        elif state == PA_CONTEXT_FAILED :
            print "Connection failed"

        elif state == PA_CONTEXT_TERMINATED:
            print "Connection terminated"

    def sink_info_cb(self, context, sink_info_p, _, __):
        if not sink_info_p:
            return

        sink_info = sink_info_p.contents
        print 'sink seen: %s / %s' % (sink_info.name, sink_info.description)

        if sink_info.name == self.sink_name:
            # Found the sink we want to monitor for peak levels.
            # Tell PA to call stream_read_cb with peak samples.
            print 'setting up peak recording using', sink_info.monitor_source_name
            samplespec = pa_sample_spec()
            samplespec.channels = 2
            samplespec.format = PA_SAMPLE_U8
            samplespec.rate = self.rate

            pa_stream = pa_stream_new(context, "peak detect demo", samplespec, None)
            pa_stream_set_read_callback(pa_stream,
                                        self._stream_read_cb,
                                        sink_info.index)
            pa_stream_connect_record(pa_stream,
                                     sink_info.monitor_source_name,
                                     None,
                                     PA_STREAM_PEAK_DETECT)

    def stream_read_cb(self, stream, length, index_incr):
        data = c_void_p()
        pa_stream_peek(stream, data, c_ulong(length))
        data = cast(data, POINTER(c_ubyte))
        for i in xrange(length):
            # When PA_SAMPLE_U8 is used, samples values range from 128
            # to 255 because the underlying audio data is signed but
            # it doesn't make sense to return signed peaks.
            self._samples.put(data[i] - 128)
        pa_stream_drop(stream)


    def flushqueue(self):
        self._samples.queue.clear()

