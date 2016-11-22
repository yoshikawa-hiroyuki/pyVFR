#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.

"""
import copy

class Base(object):
    """
    リンクオブジェクト基底クラス
    相互参照リンク機能を持つオブジェクトの基底クラスです．
      _alive: 有効／無効フラグ
      _Ref[]: 参照リンクリスト
      _doSuicide: 自己破壊モード．参照リンクのカウントが0になった時に，
      　　　　　　　自分自身を無効化します．
    """

    def __init__(self, suicide =False):
        self._alive = True
        self._Ref = []
        self._doSuicide = suicide

    def __del__(self, object=object):
        self.destroy()

    def __str__(self):
        rs = str(self.__class__) + '<#ref=' + str(len(self._Ref))
        if self._alive: rs += ' alive'
        else: rs += ' dead'
        if self._doSuicide: rs += ' suicide'
        rs += '>'
        return rs

    def destroy(self):
        """
        無効化
        _aliveをFalseに設定し，_Refの各要素のrumor()を呼び出します．
        """
        if not self._alive: return
        self._alive = False
        refs = copy.copy(self._Ref)
        for r in refs:
            r.rumor(self)
        del refs, self._Ref[:]

    def getSuicideMode(self):
        """
        自己破壊モードを返す
        """
        return self._doSuicide

    def setSuicideMode(self, suicide):
        """
        自己破壊モードの設定
        - suicide: 自己破壊モード
        """
        if self._doSuicide == suicide: return
        self._doSuicide = suicide

    def addRef(self, ref):
        """
        参照リンクへの追加
        - ref: 追加する参照リンク
        """
        if ref is None: return
        if ref is self: return
        self._Ref.append(ref)

    def remRef(self, dref):
        """
        参照リンクからの削除
        - dref: 削除する参照リンク
        """
        if dref is None: return False
        if dref in self._Ref:
            self._Ref.remove(dref)
            if len(self._Ref) < 1 and self._doSuicide :
                self.destroy()
            return True
        return False

    def rumor(self, ref):
        """
        参照先からの破壊通知を受け取リます．参照先のdestroy()から自動的に
        呼び出されます．
        派生クラスにおいて実装されます．
        - ref: 破壊されたオブジェクトへの参照
        """
        pass

    def notice(self, invalidateDL =True):
        """
        変更通知
        _Refの各要素のnotice()を呼び出します．
        - invalidateDL: ディスプレイリスト無効化モード(派生クラスで使用します)
        """
        for r in self._Ref:
            r.notice(invalidateDL)

    def chkNotice(self):
        """
        変更検査要求
        _Refの各要素のchkNotice()を呼び出します．
        """
        for r in self._Ref:
            r.chkNotice()


class Node(Base):
    """
    ノードクラス
    相互参照リンク機能を持つオブジェクト(ノード)のクラスです．
      _id: ID番号．全てのNodeクラスの派生クラスを通じて，ユニークな整数が
           割り振られます．
      _name: ノード名．指定しない場合は'%%noname%%'に設定されます．
    """

    """ノードシーケンシャル番号"""
    _sequence = 0

    """ノード名初期値"""
    _NONAME = '%%noname%%'
    
    def __init__(self, name =_NONAME, suicide =False):
        Base.__init__(self, suicide)
        Node._sequence += 1
        self._id = Node._sequence
        self._name = name
        
    def __del__(self):
        Base.__del__(self)

    def __str__(self):
        rs = str(self.__class__)
        rs += '<_id=' + str(self._id) + ' _name=' + self._name + ' '
        rs += Base.__str__(self).replace(str(self.__class__), '')
        rs += '>'
        return rs

    def getName(self):
        """
        名前を返す．
        """
        return self._name

    def setName(self, name):
        """
        名前を設定する．
        - name: 設定する名前
        """
        if name is None or name == '':
            self._name = _NONAME
        else:
            self._name = name

    def getID(self):
        """
        ID番号を返す．
        """
        return self._id

    def rumor(self, ref):
        """
        参照先からの破壊通知を受け取リます．参照先のdestroy()から自動的に
        呼び出されます．
        基底クラスのrumor()を呼び出します．
        - ref: 破壊されたオブジェクトへの参照
        """
        Base.rumor(self, ref)

    def getNodeById(self, id):
        """
        ID番号によるノード検索
        指定されたID番号を持つノードを，自分自身を含む配下のノードから
        検索します．
        - id: 検索対象のノードID番号
        """
        if self._id == id : return self
        return None

    def getNodeByName(self, name):
        """
        名前によるノード検索
        指定されたノード名を持つ最初のノードを，自分自身を含む配下のノードから
        検索します．
        - name: 検索対象のノード名
        """
        if self._name == name : return self
        return None

    def xstring(self, ts =0):
        """
        ノードの階層表示用文字列を返す．
        - ts: タブオーダー
        """
        rs = ' ' * ts + self.__str__() + '\n'
        return rs


class Group(Node):
    """
    グルーピングノードクラス
    複数の子供のノードを持つ事ができるグルーピングノードのクラスです．
      _children[]: 子供ノードへの参照リスト
    """
    def __init__(self, name =Node._NONAME, suicide =False):
        Node.__init__(self, name, suicide)
        self._children = []

    def __del__(self):
        Node.__del__(self)

    def __str__(self):
        rs = str(self.__class__) + '<#child=' + str(len(self._children)) + ' '
        rs += Node.__str__(self).replace(str(self.__class__), '')
        rs += '>'
        return rs

    def destroy(self):
        """
        無効化
        全ての子供ノードへの参照を削除し，基底クラスのdestroy()を呼び出します．
        """
        self.remAllChildren()
        Node.destroy(self)

    def rumor(self, ref):
        """
        参照先からの破壊通知を受け取リます．参照先のdestroy()から自動的に
        呼び出されます．
        呼び出し元が子供ノードリストに含まれていれば，参照を削除します．
        - ref: 破壊されたオブジェクトへの参照
        """
        self.remChild(ref)

    def addChild(self, node):
        """
        子供ノードの追加
        追加に成功すればTrueを，失敗すればFalseを返します．
        - node: 追加する子供ノードへの参照
        """
        if not '_alive' in dir(node) or not node._alive: return
        if node is self: return False
        self._children.append(node)
        node.addRef(self)
        self.notice()
        return True

    def remChild(self, node):
        """
        子供ノードの削除
        削除に成功すればTrueを，失敗すればFalseを返します．
        - node: 削除する子供ノードへの参照
        """
        if node is None: return False
        if node in self._children:
            self._children.remove(node)
            node.remRef(self)
            self.notice()
            return True
        return False

    def remAllChildren(self):
        """
        全ての子供ノードの削除
        全ての子供ノードへの参照を削除します．
        """
        chlds = copy.copy(self._children)
        for c in chlds:
            c.remRef(self)
        del chlds, self._children[:]

    def getNumChildren(self):
        """
        子供のノードの数を返す．
        """
        return len(self._children)

    def getChild(self, idx):
        """
        idx番目の子供のノードを返す．
        - idx: 子供のノードのインデックス番号
        """
        try:
            return self._children[idx]
        except:
            return None

    def getNodeById(self, id):
        """
        ID番号によるノード検索
        指定されたID番号を持つノードを，自分自身と子供のノード配下から検索
        します．
        - id: 検索対象のノードID番号
        """
        if id == self._id: return self
        for c in self._children:
            ret = c.getNodeById(id)
            if ret: return ret
        return None
    
    def getNodeByName(self, name):
        """
        名前によるノード検索
        指定されたノード名を持つ最初のノードを，自分自身と子供ノード配下から
        検索します．
        - name: 検索対象のノード名
        """
        if self._name == name : return self
        for c in self._children:
            ret = c.getNodeByName(name)
            if ret: return ret
        return None

    def xstring(self, ts =0):
        """
        ノードの階層表示用文字列を返す．
        - ts: タブオーダー
        """
        rs = ' ' * ts + self.__str__() + '\n'
        for c in self._children:
            rs += c.xstring(ts+2)
        return rs
