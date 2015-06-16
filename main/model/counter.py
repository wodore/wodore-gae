from google.appengine.ext import ndb

import util

class CountableLazy(object):
  """A mixin that adds countability to a class.
  The *lazy* counter can undercount a bit.

  Adds a 'cnt' property which is accesses as 'count' property.
  Adds a 'count_incr()' and 'count_decr()' method.
  """
  cnt = ndb.IntegerProperty(default=0, indexed=True, required=True)

  _incr = 0

  @property
  def count(self):
    return self.cnt + self._incr


  def incr(self,step=1):
    self._incr += step

  def decr(self,step=1):
    self.incr(-step)

  #def _post_get_hook(self):
    #pass
    #self._orig_collision = future.get_result().collision
    #  if getattr(self,'collision',None):
    #    self._orig_collision = self.collision
    #  else:
    #    self._orig_collision = False

  def _pre_put_hook(self):
    if getattr(self,'toplevel',None):
      if getattr(self,'_orig_collection',None):
        if self._orig_collection != self.collection:
          raise UserWarning("It is not possible to have different collection values \
          The 'get' collection value was: {col1}, but now it is {col2}". \
            format( col1=self._orig_collection,col2=self.collection))

      top = self.toplevel.get()
      top.incr(self._incr)
      top.put()
    self.cnt += self._incr
    self._incr = 0

  @classmethod
  def get_counter_dbs(
      cls, cnt=None, count=None, **kwargs
    ):
    """ Call this function when 'CountableLazy' is used in the 'get_dbs' function.
    """
    cnt = cnt or count or \
     util.param('cnt') or util.param('count')
    if str(cnt).isdigit():
      cnt = int(cnt)
    elif cnt:
      cnt = cnt.split(':')
      if cnt[0] != 'IN':
        value = int(cnt[1])
      else:
        value = [int(i) for i in cnt[1].split(',')]
      cnt_dic = {"test" : cnt[0],
        "value" : value}
      kwargs["cnt"] = cnt_dic
      return kwargs
    kwargs["cnt"] = int(cnt) if str(cnt).isdigit() else cnt
    return kwargs



#TODO: sharded counter if needed
